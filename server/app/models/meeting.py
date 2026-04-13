"""会议模型 — Meeting + MeetingAttendee + MeetingMinutes"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.community import gen_id


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("MT"))
    community_id: Mapped[str] = mapped_column(String(32), ForeignKey("communities.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    meeting_type: Mapped[str] = mapped_column(String(20), default="committee")  # committee/owner_assembly
    location: Mapped[str] = mapped_column(String(200), default="")  # 地点或线上链接
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")  # scheduled/ongoing/ended/cancelled
    created_by: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    community = relationship("Community", back_populates="meetings")
    creator = relationship("User", foreign_keys=[created_by])
    attendees = relationship("MeetingAttendee", back_populates="meeting", lazy="selectin", cascade="all, delete-orphan")
    minutes = relationship("MeetingMinutes", back_populates="meeting", lazy="noload", cascade="all, delete-orphan")


class MeetingAttendee(Base):
    __tablename__ = "meeting_attendees"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("MA"))
    meeting_id: Mapped[str] = mapped_column(String(32), ForeignKey("meetings.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    rsvp_status: Mapped[str] = mapped_column(String(20), default="pending")  # pending/confirmed/declined
    checked_in: Mapped[bool] = mapped_column(Boolean, default=False)
    checked_in_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    meeting = relationship("Meeting", back_populates="attendees")
    user = relationship("User")


class MeetingMinutes(Base):
    __tablename__ = "meeting_minutes"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("MM"))
    meeting_id: Mapped[str] = mapped_column(String(32), ForeignKey("meetings.id"), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, default="")  # 会议纪要内容
    recording_url: Mapped[str] = mapped_column(String(500), default="")  # 录音URL
    is_final: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否为正式版
    signed_by: Mapped[str] = mapped_column(Text, default="[]")  # JSON: 签名委员列表
    created_by: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    meeting = relationship("Meeting", back_populates="minutes")
    creator = relationship("User", foreign_keys=[created_by])
