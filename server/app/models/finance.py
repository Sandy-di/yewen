"""财务模型 — FinanceReport + FinanceItem"""

import json
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.community import gen_id


class FinanceReport(Base):
    __tablename__ = "finance_reports"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("F"))
    community_id: Mapped[str] = mapped_column(String(32), ForeignKey("communities.id"), nullable=False, index=True)
    month: Mapped[str] = mapped_column(String(10), nullable=False)  # 2026-03
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending / published / rejected
    submitted_by: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    approved_by: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=True, default=None)
    approved_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=None)
    total_income: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total_expense: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    attachments: Mapped[str] = mapped_column(Text, default="[]")  # JSON: [{name, url, size}]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    community = relationship("Community", back_populates="finance_reports")
    submitter = relationship("User", foreign_keys=[submitted_by])
    approver = relationship("User", foreign_keys=[approved_by])
    items = relationship("FinanceItem", back_populates="report", lazy="selectin", cascade="all, delete-orphan")

    def get_attachments(self) -> list[dict]:
        """解析 attachments JSON"""
        try:
            return json.loads(self.attachments or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    def set_attachments(self, value: list[dict]) -> None:
        """设置 attachments JSON"""
        self.attachments = json.dumps(value, ensure_ascii=False)


class FinanceItem(Base):
    __tablename__ = "finance_items"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("FI"))
    report_id: Mapped[str] = mapped_column(String(32), ForeignKey("finance_reports.id"), nullable=False, index=True)
    item_type: Mapped[str] = mapped_column(String(10), nullable=False)  # income / expense
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(200), default="")

    # 关系
    report = relationship("FinanceReport", back_populates="items")
