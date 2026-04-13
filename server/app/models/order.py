"""工单模型 — RepairOrder + OrderTimeline"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.community import gen_id


class RepairOrder(Base):
    __tablename__ = "repair_orders"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("WR"))
    community_id: Mapped[str] = mapped_column(String(32), ForeignKey("communities.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(30), nullable=False)  # access / facility / water_elec / green / other
    sub_category: Mapped[str] = mapped_column(String(50), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    photos: Mapped[str] = mapped_column(Text, default="[]")  # JSON array string
    status: Mapped[str] = mapped_column(String(20), default="submitted")  # submitted / accepted / processing / pending_check / completed / rework
    property_id: Mapped[str] = mapped_column(String(32), ForeignKey("user_properties.id"), nullable=True)
    contact_phone: Mapped[str] = mapped_column(String(20), default="")
    accepted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    accepted_by: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=True, default=None)
    acceptor_phone: Mapped[str] = mapped_column(String(20), default="")
    estimated_time: Mapped[str] = mapped_column(String(20), default="")
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    completion_photos: Mapped[str] = mapped_column(Text, default="[]")
    completion_note: Mapped[str] = mapped_column(Text, default="")
    video: Mapped[str] = mapped_column(String(500), default="")  # 视频URL
    appointment_time: Mapped[str] = mapped_column(String(30), default="")  # 预约上门时间
    rating: Mapped[int] = mapped_column(Integer, nullable=True, default=None)
    rating_comment: Mapped[str] = mapped_column(Text, default="")
    sla_level: Mapped[int] = mapped_column(Integer, default=24)  # 小时
    sla_deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # 关系
    community = relationship("Community", back_populates="orders")
    user = relationship("User", foreign_keys=[user_id])
    property_ref = relationship("UserProperty", foreign_keys=[property_id])
    acceptor = relationship("User", foreign_keys=[accepted_by])
    timelines = relationship("OrderTimeline", back_populates="order", lazy="selectin", cascade="all, delete-orphan")


class OrderTimeline(Base):
    __tablename__ = "order_timelines"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("T"))
    order_id: Mapped[str] = mapped_column(String(32), ForeignKey("repair_orders.id"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)  # submitted / accepted / processing / completed / verified
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    order = relationship("RepairOrder", back_populates="timelines")
