"""档案模型 — Archive"""

import json
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.community import gen_id


class Archive(Base):
    __tablename__ = "archives"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("AR"))
    community_id: Mapped[str] = mapped_column(String(32), ForeignKey("communities.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    file_url: Mapped[str] = mapped_column(String(500), default="")  # 文件URL
    file_name: Mapped[str] = mapped_column(String(200), default="")
    file_hash: Mapped[str] = mapped_column(String(64), default="")  # 文件哈希（防篡改）
    category: Mapped[str] = mapped_column(String(50), default="other")  # contract/resolution/approval/lawsuit/other
    access_level: Mapped[str] = mapped_column(String(20), default="public")  # public/internal/confidential
    tags: Mapped[str] = mapped_column(Text, default="[]")  # JSON array of tags
    uploaded_by: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # 关系
    community = relationship("Community", back_populates="archives")
    uploader = relationship("User", foreign_keys=[uploaded_by])

    def get_tags(self) -> list[str]:
        try:
            return json.loads(self.tags or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    def set_tags(self, value: list[str]) -> None:
        self.tags = json.dumps(value, ensure_ascii=False)
