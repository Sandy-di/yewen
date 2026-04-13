"""投诉路由 — CRUD + 回复 + 标记重要"""

import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.models import User
from app.middleware.auth import get_current_user, require_role
from app.schemas.complaint import (
    ComplaintListOut, ComplaintDetailOut, ComplaintReplyOut,
    ComplaintCreate, ComplaintCreateResponse, ComplaintReplyCreate,
    ComplaintMarkImportant,
)
from app.services.complaint_service import ComplaintService

router = APIRouter()


def complaint_to_list_out(c: Complaint, reply_count: int = 0) -> ComplaintListOut:
    """ORM → 列表输出"""
    return ComplaintListOut(
        complaintId=c.id,
        title=c.title,
        category=c.category,
        status=c.status,
        isImportant=c.is_important,
        slaDeadline=c.sla_deadline,
        createdAt=c.created_at,
        replyCount=reply_count,
    )


@router.get("", response_model=dict)
async def get_complaint_list(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取投诉列表"""
    service = ComplaintService(db)
    complaints, total = await service.get_list(
        current_user,
        status=status,
        category=category,
        keyword=keyword,
        page=page,
        page_size=pageSize,
    )
    outs = []
    for c in complaints:
        out = complaint_to_list_out(c, reply_count=len(c.replies))
        outs.append(out.model_dump())
    return {"data": outs, "total": total, "page": page, "pageSize": pageSize}


@router.get("/{complaint_id}", response_model=ComplaintDetailOut)
async def get_complaint_detail(
    complaint_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取投诉详情"""
    service = ComplaintService(db)
    complaint = await service.get_by_id(complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="投诉不存在")

    # 权限：业主只能看自己的
    if current_user.role == "owner" and complaint.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此投诉")

    base = complaint_to_list_out(complaint, reply_count=len(complaint.replies))
    replies = [
        ComplaintReplyOut(
            id=r.id,
            userId=r.user_id,
            content=r.content,
            replyType=r.reply_type,
            createdAt=r.created_at,
        )
        for r in complaint.replies
    ]

    return ComplaintDetailOut(
        **base.model_dump(),
        content=complaint.content,
        photos=json.loads(complaint.photos) if isinstance(complaint.photos, str) else complaint.photos,
        userId=complaint.user_id,
        resolvedAt=complaint.resolved_at,
        replies=replies,
    )


@router.post("", response_model=ComplaintCreateResponse)
async def create_complaint(
    req: ComplaintCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交投诉（业主）"""
    service = ComplaintService(db)
    complaint = await service.create(current_user, req)
    return ComplaintCreateResponse(success=True, complaintId=complaint.id)


@router.post("/{complaint_id}/reply")
async def reply_complaint(
    complaint_id: str,
    req: ComplaintReplyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """回复投诉（物业回复/业委会督导/业委会结案）"""
    service = ComplaintService(db)
    try:
        # reply_type=resolve 仅业委会可用
        if req.replyType == "resolve" and current_user.role != "committee":
            raise HTTPException(status_code=403, detail="仅业委会可结案")
        if req.replyType == "supervise" and current_user.role != "committee":
            raise HTTPException(status_code=403, detail="仅业委会可督导")
        await service.reply(complaint_id, current_user, req.content, req.replyType)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}


@router.put("/{complaint_id}/important")
async def mark_important(
    complaint_id: str,
    req: ComplaintMarkImportant,
    current_user: User = Depends(require_role("committee")),
    db: AsyncSession = Depends(get_db),
):
    """标记投诉为重要（仅业委会）"""
    service = ComplaintService(db)
    try:
        await service.mark_important(complaint_id, req.isImportant)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}


@router.post("/{complaint_id}/close")
async def close_complaint(
    complaint_id: str,
    current_user: User = Depends(require_role("committee")),
    db: AsyncSession = Depends(get_db),
):
    """关闭投诉（仅业委会）"""
    service = ComplaintService(db)
    try:
        await service.close(complaint_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}
