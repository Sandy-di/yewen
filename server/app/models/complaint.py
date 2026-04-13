"""投诉模型 — Complaint + ComplaintReply"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.community import gen_id


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("CP"))
    community_id: Mapped[str] = mapped_column(String(32), ForeignKey("communities.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(30), default="other")  # service/fee/safety/environment/other
    photos: Mapped[str] = mapped_column(Text, default="[]")  # JSON array
    status: Mapped[str] = mapped_column(String(20), default="submitted")  # submitted/replied/resolved/closed
    is_important: Mapped[bool] = mapped_column(Boolean, default=False)  # 业委会标记重要
    sla_hours: Mapped[int] = mapped_column(Integer, default=48)  # 物业回复SLA(小时)
    sla_deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    resolved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # 关系
    community = relationship("Community", back_populates="complaints")
    user = relationship("User", foreign_keys=[user_id])
    replies = relationship("ComplaintReply", back_populates="complaint", lazy="selectin", cascade="all, delete-orphan")


class ComplaintReply(Base):
    __tablename__ = "complaint_replies"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("CR"))
    complaint_id: Mapped[str] = mapped_column(String(32), ForeignKey("complaints.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    reply_type: Mapped[str] = mapped_column(String(20), default="reply")  # reply/supervise/resolve
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    complaint = relationship("Complaint", back_populates="replies")
    user = relationship("User")
