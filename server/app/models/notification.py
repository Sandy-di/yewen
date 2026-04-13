"""通知模型 — Notification + NotificationSubscription"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.community import gen_id


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("N"))
    community_id: Mapped[str] = mapped_column(String(32), ForeignKey("communities.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, default="")
    type: Mapped[str] = mapped_column(String(20), default="info")  # urgent/important/info/activity
    biz_type: Mapped[str] = mapped_column(String(20), default="")  # vote/order/finance/announcement/complaint
    biz_id: Mapped[str] = mapped_column(String(32), default="")  # 关联业务ID
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    user = relationship("User", foreign_keys=[user_id])


class NotificationSubscription(Base):
    """用户订阅的消息类型"""
    __tablename__ = "notification_subscriptions"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("NS"))
    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    msg_type: Mapped[str] = mapped_column(String(30), nullable=False)  # vote_remind/order_update/finance_publish/announcement/complaint_reply
    is_subscribed: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    user = relationship("User")
