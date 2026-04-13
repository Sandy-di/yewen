"""社区模型"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


def gen_id(prefix: str) -> str:
    return f"{prefix}{datetime.now(timezone.utc).strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"


class Community(Base):
    __tablename__ = "communities"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("C"))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    total_units: Mapped[int] = mapped_column(Integer, default=0)
    total_area: Mapped[float] = mapped_column(Float, default=0.0)
    address: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    users = relationship("User", back_populates="community", lazy="selectin")
    votes = relationship("Vote", back_populates="community", lazy="selectin")
    orders = relationship("RepairOrder", back_populates="community", lazy="selectin")
    finance_reports = relationship("FinanceReport", back_populates="community", lazy="selectin")
    announcements = relationship("Announcement", back_populates="community", lazy="selectin")
