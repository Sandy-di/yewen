"""通知 Schema"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class NotificationOut(BaseModel):
    """通知输出"""
    id: str
    title: str
    content: str = ""
    type: str  # urgent/important/info/activity
    bizType: str = ""
    bizId: str = ""
    isRead: bool = False
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationListOut(BaseModel):
    data: List[NotificationOut]
    total: int
    unreadCount: int = 0


class SubscriptionUpdate(BaseModel):
    """更新订阅"""
    msgType: str  # vote_remind/order_update/finance_publish/announcement/complaint_reply
    isSubscribed: bool
