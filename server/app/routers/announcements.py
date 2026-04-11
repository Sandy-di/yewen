"""公告路由 — CRUD + 阅读统计"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Announcement, AnnouncementRead, User, Community
from app.middleware.auth import get_current_user, require_role
from app.schemas.announcement import (
    AnnouncementListOut, AnnouncementDetailOut, AnnouncementCreate,
)

router = APIRouter()


def announcement_to_list_out(ann: Announcement, read_count: int = 0, total_users: int = 0) -> AnnouncementListOut:
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取公告列表"""
    query = select(Announcement)
    if current_user.community_id:
        query = query.where(Announcement.community_id == current_user.community_id)
    # 置顶优先，然后按时间倒序
    query = query.order_by(Announcement.is_top.desc(), Announcement.created_at.desc())

    result = await db.execute(query)
    announcements = result.scalars().all()

    # 获取社区总人数
    total_users = 0
    if current_user.community_id:
        user_count_result = await db.execute(
            select(func.count(User.id)).where(User.community_id == current_user.community_id)
        )
        total_users = user_count_result.scalar() or 0

    ann_outs = []
    for ann in announcements:
        # 获取阅读数
        read_result = await db.execute(
            select(func.count(AnnouncementRead.id)).where(AnnouncementRead.announcement_id == ann.id)
        )
        read_count = read_result.scalar() or 0
        ann_outs.append(announcement_to_list_out(ann, read_count, total_users))

    return {"data": ann_outs, "total": len(ann_outs)}


@router.get("/{ann_id}", response_model=AnnouncementDetailOut)
async def get_announcement_detail(
    ann_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取公告详情（自动记录阅读）"""
    result = await db.execute(select(Announcement).where(Announcement.id == ann_id))
    ann = result.scalar_one_or_none()
    if not ann:
        raise HTTPException(status_code=404, detail="公告不存在")

    # 记录阅读
    exist = await db.execute(
        select(AnnouncementRead).where(
            AnnouncementRead.announcement_id == ann_id,
            AnnouncementRead.user_id == current_user.id,
        )
    )
    if not exist.scalar_one_or_none():
        read_record = AnnouncementRead(
            announcement_id=ann_id,
            user_id=current_user.id,
        )
        db.add(read_record)
        await db.flush()

    # 获取阅读数
    read_result = await db.execute(
        select(func.count(AnnouncementRead.id)).where(AnnouncementRead.announcement_id == ann_id)
    )
    read_count = read_result.scalar() or 0

    total_users = 0
    if current_user.community_id:
        user_count_result = await db.execute(
            select(func.count(User.id)).where(User.community_id == current_user.community_id)
        )
        total_users = user_count_result.scalar() or 0

    base = announcement_to_list_out(ann, read_count, total_users)
    return AnnouncementDetailOut(**base.model_dump(), content=ann.content)


@router.post("")
async def create_announcement(
    req: AnnouncementCreate,
    current_user: User = Depends(require_role("property", "committee")),
    db: AsyncSession = Depends(get_db),
):
    """发布公告（物业/业委会）"""
    ann = Announcement(
        community_id=current_user.community_id,
        title=req.title,
        content=req.content,
        type=req.type,
        publisher=req.publisher,
        publisher_name=req.publisherName or current_user.nickname,
        is_top=req.isTop,
        created_by=current_user.id,
    )
    db.add(ann)
    await db.flush()

    return {"success": True, "id": ann.id}
