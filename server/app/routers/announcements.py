"""公告路由 — CRUD + 阅读统计"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.models import User
from app.middleware.auth import get_current_user, require_role
from app.schemas.announcement import (
    AnnouncementListOut, AnnouncementDetailOut, AnnouncementCreate,
    AnnouncementUpdate,
)
from app.services.announcement_service import AnnouncementService

router = APIRouter()


def announcement_to_list_out(ann, read_count: int = 0, total_users: int = 0) -> AnnouncementListOut:
    """ORM → 列表输出"""
    return AnnouncementListOut(
        id=ann.id,
        title=ann.title,
        type=ann.type,
        publisher=ann.publisher,
        publisherName=ann.publisher_name,
        isTop=ann.is_top,
        readCount=read_count,
        totalUsers=total_users,
        createdAt=ann.created_at,
    )


@router.get("", response_model=dict)
async def get_announcement_list(
    type: Optional[str] = Query(None, alias="type"),
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取公告列表"""
    service = AnnouncementService(db)
    items, total = await service.get_list(
        current_user.community_id,
        type_=type,
        keyword=keyword,
        page=page,
        page_size=pageSize,
    )
    ann_outs = [
        announcement_to_list_out(
            item["announcement"], item["read_count"], item["total_users"]
        ).model_dump()
        for item in items
    ]
    return {"data": ann_outs, "total": total, "page": page, "pageSize": pageSize}


@router.get("/{ann_id}", response_model=AnnouncementDetailOut)
async def get_announcement_detail(
    ann_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取公告详情（自动记录阅读）"""
    service = AnnouncementService(db)
    result = await service.get_by_id(ann_id, current_user)
    if not result:
        raise HTTPException(status_code=404, detail="公告不存在")

    ann = result["announcement"]
    base = announcement_to_list_out(ann, result["read_count"], result["total_users"])
    return AnnouncementDetailOut(**base.model_dump(), content=ann.content)


@router.post("")
async def create_announcement(
    req: AnnouncementCreate,
    current_user: User = Depends(require_role("property", "committee")),
    db: AsyncSession = Depends(get_db),
):
    """发布公告（物业/业委会）"""
    service = AnnouncementService(db)
    ann = await service.create(current_user, req)
    return {"success": True, "id": ann.id}


@router.put("/{ann_id}")
async def update_announcement(
    ann_id: str,
    req: AnnouncementUpdate,
    current_user: User = Depends(require_role("property", "committee")),
    db: AsyncSession = Depends(get_db),
):
    """编辑公告（物业/业委会）"""
    service = AnnouncementService(db)
    ann = await service.update(ann_id, req)
    if not ann:
        raise HTTPException(status_code=404, detail="公告不存在")
    return {"success": True}


@router.delete("/{ann_id}")
async def delete_announcement(
    ann_id: str,
    current_user: User = Depends(require_role("property", "committee")),
    db: AsyncSession = Depends(get_db),
):
    """删除公告（物业/业委会）"""
    service = AnnouncementService(db)
    deleted = await service.delete(ann_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="公告不存在")
    return {"success": True}
