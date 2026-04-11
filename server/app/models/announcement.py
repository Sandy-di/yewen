"""公告模型 — Announcement + AnnouncementRead"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.community import gen_id


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("A"))
    community_id: Mapped[str] = mapped_column(String(32), ForeignKey("communities.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, default="")
    type: Mapped[str] = mapped_column(String(20), default="notice")  # vote / notice / finance
    publisher: Mapped[str] = mapped_column(String(20), default="物业")  # 物业 / 业委会
    publisher_name: Mapped[str] = mapped_column(String(50), default="")
    is_top: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 关系
    community = relationship("Community", back_populates="announcements")
    creator = relationship("User", foreign_keys=[created_by])
    reads = relationship("AnnouncementRead", back_populates="announcement", lazy="noload", cascade="all, delete-orphan")


class AnnouncementRead(Base):
    __tablename__ = "announcement_reads"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("AR"))
    announcement_id: Mapped[str] = mapped_column(String(32), ForeignKey("announcements.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 关系
    announcement = relationship("Announcement", back_populates="reads")
    user = relationship("User")
