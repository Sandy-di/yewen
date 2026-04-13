"""通知路由 — 列表/已读/订阅管理"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.middleware.auth import get_current_user
from app.schemas.notification import NotificationOut, SubscriptionUpdate
from app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=dict)
async def get_notifications(
    isRead: bool | None = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取通知列表"""
    service = NotificationService(db)
    items, total, unread_count = await service.get_list(
        current_user.id, is_read=isRead, page=page, page_size=pageSize
    )
    outs = [
        NotificationOut(
            id=n.id,
            title=n.title,
            content=n.content,
            type=n.type,
            bizType=n.biz_type,
            bizId=n.biz_id,
            isRead=n.is_read,
            createdAt=n.created_at,
        ).model_dump()
        for n in items
    ]
    return {"data": outs, "total": total, "unreadCount": unread_count, "page": page, "pageSize": pageSize}


@router.put("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """标记通知已读"""
    service = NotificationService(db)
    await service.mark_read(notification_id, current_user.id)
    return {"success": True}


@router.put("/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """全部标记已读"""
    service = NotificationService(db)
    await service.mark_all_read(current_user.id)
    return {"success": True}


@router.get("/subscriptions", response_model=dict)
async def get_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取消息订阅设置"""
    service = NotificationService(db)
    subs = await service.get_subscriptions(current_user.id)
    return {
        "data": [
            {"msgType": s.msg_type, "isSubscribed": s.is_subscribed}
            for s in subs
        ]
    }


@router.put("/subscriptions")
async def update_subscription(
    req: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新消息订阅"""
    service = NotificationService(db)
    await service.update_subscription(current_user.id, req.msgType, req.isSubscribed)
    return {"success": True}
