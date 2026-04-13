"""投票路由 — CRUD + 投票提交 + 结果计算"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.models import User
from app.middleware.auth import get_current_user, require_role
from app.schemas.vote import (
    VoteListOut, VoteDetailOut, VoteOptionOut,
    VoteCreate, VoteSubmit, VoteSubmitResponse, VoteCreateResponse,
)
from app.services.vote_service import VoteService

router = APIRouter()


def vote_to_list_out(vote) -> VoteListOut:
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


@router.get("", response_model=dict)
async def get_vote_list(
    status: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取投票列表"""
    service = VoteService(db)
    votes, total = await service.get_list(
        current_user.community_id,
        status=status,
        keyword=keyword,
        page=page,
        page_size=pageSize,
    )
    vote_outs = [vote_to_list_out(v).model_dump() for v in votes]
    return {"data": vote_outs, "total": total, "page": page, "pageSize": pageSize}


@router.get("/{vote_id}", response_model=VoteDetailOut)
async def get_vote_detail(
    vote_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取投票详情"""
    service = VoteService(db)
    vote = await service.get_by_id(vote_id)
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
    service = VoteService(db)
    vote = await service.create(current_user, req)
    return VoteCreateResponse(success=True, voteId=vote.id)


@router.post("/{vote_id}/submit", response_model=VoteSubmitResponse)
async def submit_vote(
    vote_id: str,
    req: VoteSubmit,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交投票"""
    service = VoteService(db)
    try:
        tx_hash = await service.submit_vote(current_user, vote_id, req.optionId)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return VoteSubmitResponse(success=True, txHash=tx_hash)
