"""投票模型 — Vote + VoteOption + VoteRecord"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.community import gen_id


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("V"))
    community_id: Mapped[str] = mapped_column(String(32), ForeignKey("communities.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    verification_level: Mapped[int] = mapped_column(Integer, default=1)  # 1-4
    vote_type: Mapped[str] = mapped_column(String(30), default="double_majority")  # double_majority / double_three_quarters
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft / active / ended / archived
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    total_properties: Mapped[int] = mapped_column(Integer, default=0)
    participated_count: Mapped[int] = mapped_column(Integer, default=0)
    participated_area: Mapped[float] = mapped_column(Float, default=0.0)
    total_area: Mapped[float] = mapped_column(Float, default=0.0)
    created_by: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=True)
    result_hash: Mapped[str] = mapped_column(String(100), nullable=True, default=None)
    result: Mapped[str] = mapped_column(String(20), nullable=True, default=None)  # passed / failed
    result_summary: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # 关系
    community = relationship("Community", back_populates="votes")
    options = relationship("VoteOption", back_populates="vote", lazy="selectin", cascade="all, delete-orphan")
    records = relationship("VoteRecord", back_populates="vote", lazy="noload", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])


class VoteOption(Base):
    __tablename__ = "vote_options"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("O"))
    vote_id: Mapped[str] = mapped_column(String(32), ForeignKey("votes.id"), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    count: Mapped[int] = mapped_column(Integer, default=0)
    area: Mapped[float] = mapped_column(Float, default=0.0)

    # 关系
    vote = relationship("Vote", back_populates="options")


class VoteRecord(Base):
    __tablename__ = "vote_records"
    __table_args__ = (
        UniqueConstraint("vote_id", "user_id", name="uq_vote_user"),
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("R"))
    vote_id: Mapped[str] = mapped_column(String(32), ForeignKey("votes.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    option_id: Mapped[str] = mapped_column(String(32), ForeignKey("vote_options.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    vote = relationship("Vote", back_populates="records")
    user = relationship("User")
    option = relationship("VoteOption")
