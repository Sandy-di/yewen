"""投票模板模型 — 预设8种标准化投票场景"""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class VoteTemplate(Base):
    __tablename__ = "vote_templates"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # 场景名称
    description: Mapped[str] = mapped_column(Text, default="")  # 场景说明
    vote_type: Mapped[str] = mapped_column(String(30), default="double_majority")  # 法定门槛
    verification_level: Mapped[int] = mapped_column(Integer, default=2)  # 建议核验等级
    options_template: Mapped[str] = mapped_column(Text, default="[]")  # JSON: 预设选项
    description_template: Mapped[str] = mapped_column(Text, default="")  # 投票说明模板
    sort_order: Mapped[int] = mapped_column(Integer, default=0)  # 排序
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
