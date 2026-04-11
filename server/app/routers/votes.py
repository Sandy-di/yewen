"""投票路由 — CRUD + 投票提交 + 结果计算"""

import hashlib
import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Vote, VoteOption, VoteRecord, User, Community
from app.middleware.auth import get_current_user, require_role
from app.schemas.vote import (
    VoteListOut, VoteDetailOut, VoteOptionOut,
    VoteCreate, VoteSubmit, VoteSubmitResponse, VoteCreateResponse,
)

router = APIRouter()


def vote_to_list_out(vote: Vote) -> VoteListOut:
    """ORM → 列表输出"""
    return VoteListOut(
        voteId=vote.id,
        title=vote.title,
        status=vote.status,
        voteType=vote.vote_type,
        verificationLevel=vote.verification_level,
        startTime=vote.start_time,
        endTime=vote.end_time,
        totalProperties=vote.total_properties,
        participatedCount=vote.participated_count,
        participatedArea=vote.participated_area,
        totalArea=vote.total_area,
        options=[VoteOptionOut(id=o.id, label=o.label, count=o.count, area=o.area) for o in vote.options],
        createdBy=vote.created_by,
        createdAt=vote.created_at,
        result=vote.result,
        resultSummary=vote.result_summary,
    )


def compute_vote_result(vote: Vote) -> tuple:
    """计算投票结果（双过半/双四分之三）"""
    total_props = vote.total_properties or 1
    total_area = vote.total_area or 1
    part_count = vote.participated_count
    part_area = vote.participated_area

    # 找到"同意"选项（通常是第一个选项，票数最多）
    agree_option = vote.options[0] if vote.options else None
    agree_count = agree_option.count if agree_option else 0
    agree_area = agree_option.area if agree_option else 0

    if vote.vote_type == "double_majority":
        # 双过半：参与户数>50% 且 参与面积>50%，同意户数>50%参与 且 同意面积>50%参与
        part_count_ratio = part_count / total_props
        part_area_ratio = part_area / total_area
        agree_count_ratio = agree_count / part_count if part_count > 0 else 0
        agree_area_ratio = agree_area / part_area if part_area > 0 else 0
        threshold = 0.5
        result_str = "passed" if (
            part_count_ratio > threshold and part_area_ratio > threshold
            and agree_count_ratio > threshold and agree_area_ratio > threshold
        ) else "failed"
        summary = (
            f"参与户数{part_count_ratio:.0%}（{part_count}/{total_props}），"
            f"参与面积{part_area_ratio:.0%}（{part_area:.0f}/{total_area:.0f}㎡）。"
            f"同意户数{agree_count_ratio:.0%}（{agree_count}/{part_count}），"
            f"同意面积{agree_area_ratio:.0%}（{agree_area:.0f}/{part_area:.0f}㎡）。"
            f"{'达到双过半标准，投票通过。' if result_str == 'passed' else '未达到双过半标准，投票未通过。'}"
        )
    elif vote.vote_type == "double_three_quarters":
        part_count_ratio = part_count / total_props
        part_area_ratio = part_area / total_area
        agree_count_ratio = agree_count / part_count if part_count > 0 else 0
        agree_area_ratio = agree_area / part_area if part_area > 0 else 0
        threshold = 0.75
        result_str = "passed" if (
            part_count_ratio > threshold and part_area_ratio > threshold
            and agree_count_ratio > threshold and agree_area_ratio > threshold
        ) else "failed"
        summary = (
            f"参与户数{part_count_ratio:.0%}（{part_count}/{total_props}），"
            f"参与面积{part_area_ratio:.0%}（{part_area:.0f}/{total_area:.0f}㎡）。"
            f"同意户数{agree_count_ratio:.0%}（{agree_count}/{part_count}），"
            f"同意面积{agree_area_ratio:.0%}（{agree_area:.0f}/{part_area:.0f}㎡）。"
            f"{'达到双四分之三标准，投票通过。' if result_str == 'passed' else '未达到双四分之三标准，投票未通过。'}"
        )
    else:
        result_str = "passed" if agree_count > (part_count - agree_count) else "failed"
        summary = f"同意{agree_count}票，投票{'通过' if result_str == 'passed' else '未通过'}。"

    # 生成结果哈希
    hash_data = json.dumps({
        "voteId": vote.id,
        "participatedCount": part_count,
        "participatedArea": part_area,
        "options": [{"label": o.label, "count": o.count, "area": o.area} for o in vote.options],
    }, sort_keys=True)
    result_hash = "0x" + hashlib.sha256(hash_data.encode()).hexdigest()[:16]

    return result_str, summary, result_hash


@router.get("", response_model=dict)
async def get_vote_list(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取投票列表"""
    # 自动结束已到期的投票
    now = datetime.now()
    result = await db.execute(
        select(Vote).where(Vote.status == "active", Vote.end_time < now)
    )
    expired_votes = result.scalars().all()
    for v in expired_votes:
        v.status = "ended"
        res, summary, hash_val = compute_vote_result(v)
        v.result = res
        v.result_summary = summary
        v.result_hash = hash_val
        db.add(v)
    if expired_votes:
        await db.flush()

    # 查询
    query = select(Vote).where(Vote.community_id == current_user.community_id)
    if status and status != "all":
        query = query.where(Vote.status == status)
    query = query.order_by(Vote.created_at.desc())

    result = await db.execute(query)
    votes = result.scalars().all()

    # 手动加载 options（确保 selectin 生效）
    vote_outs = []
    for v in votes:
        vote_outs.append(vote_to_list_out(v))

    return {"data": vote_outs, "total": len(vote_outs)}


@router.get("/{vote_id}", response_model=VoteDetailOut)
async def get_vote_detail(
    vote_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取投票详情"""
    result = await db.execute(select(Vote).where(Vote.id == vote_id))
    vote = result.scalar_one_or_none()
    if not vote:
        raise HTTPException(status_code=404, detail="投票不存在")

    base = vote_to_list_out(vote)
    return VoteDetailOut(
        **base.model_dump(),
        description=vote.description,
        resultHash=vote.result_hash,
    )


@router.post("", response_model=VoteCreateResponse)
async def create_vote(
    req: VoteCreate,
    current_user: User = Depends(require_role("committee")),
    db: AsyncSession = Depends(get_db),
):
    """创建投票（仅业委会）"""
    # 获取社区信息
    community = None
    if current_user.community_id:
        result = await db.execute(select(Community).where(Community.id == current_user.community_id))
        community = result.scalar_one_or_none()

    vote = Vote(
        community_id=current_user.community_id,
        title=req.title,
        description=req.description,
        verification_level=req.verificationLevel,
        vote_type=req.voteType,
        status="active",
        start_time=req.startTime or datetime.now(),
        end_time=req.endTime,
        total_properties=community.total_units if community else 0,
        total_area=community.total_area if community else 0,
        created_by=current_user.id,
    )
    db.add(vote)
    await db.flush()

    # 创建选项
    for opt in req.options:
        option = VoteOption(
            vote_id=vote.id,
            label=opt.label,
            count=0,
            area=0,
        )
        db.add(option)

    await db.flush()
    return VoteCreateResponse(success=True, voteId=vote.id)


@router.post("/{vote_id}/submit", response_model=VoteSubmitResponse)
async def submit_vote(
    vote_id: str,
    req: VoteSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交投票"""
    # 检查投票
    result = await db.execute(select(Vote).where(Vote.id == vote_id))
    vote = result.scalar_one_or_none()
    if not vote:
        raise HTTPException(status_code=404, detail="投票不存在")
    if vote.status != "active":
        raise HTTPException(status_code=400, detail="投票未在进行中")

    # 检查核验等级
    if current_user.verified_level < vote.verification_level:
        raise HTTPException(status_code=403, detail=f"需要L{vote.verification_level}核验等级")

    # 检查重复
    exist = await db.execute(
        select(VoteRecord).where(
            VoteRecord.vote_id == vote_id,
            VoteRecord.user_id == current_user.id,
        )
    )
    if exist.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="您已投过票")

    # 检查选项
    opt_result = await db.execute(select(VoteOption).where(VoteOption.id == req.optionId))
    option = opt_result.scalar_one_or_none()
    if not option or option.vote_id != vote_id:
        raise HTTPException(status_code=400, detail="无效的选项")

    # 获取用户房产面积
    user_area = 0
    from app.models import UserProperty
    prop_result = await db.execute(
        select(UserProperty).where(UserProperty.user_id == current_user.id)
    )
    for prop in prop_result.scalars().all():
        user_area += prop.usable_area

    # 事务：插入记录 + 更新计数
    record = VoteRecord(
        vote_id=vote_id,
        user_id=current_user.id,
        option_id=req.optionId,
    )
    db.add(record)

    option.count += 1
    option.area += user_area
    db.add(option)

    vote.participated_count += 1
    vote.participated_area += user_area
    db.add(vote)

    await db.flush()

    # 生成模拟哈希
    import hashlib as hl
    tx_hash = "0x" + hl.sha256(f"{vote_id}{current_user.id}{req.optionId}".encode()).hexdigest()[:12]

    return VoteSubmitResponse(success=True, txHash=tx_hash)
