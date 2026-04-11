"""房产模型"""

from datetime import datetime
from sqlalchemy import String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.community import gen_id


class UserProperty(Base):
    __tablename__ = "user_properties"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: gen_id("P"))
    user_id: Mapped[str] = mapped_column(String(32), ForeignKey("users.id"), nullable=False, index=True)
    community_id: Mapped[str] = mapped_column(String(32), ForeignKey("communities.id"), nullable=False)
    building: Mapped[str] = mapped_column(String(20), default="")
    unit: Mapped[str] = mapped_column(String(20), default="")
    room_no: Mapped[str] = mapped_column(String(20), default="")
    usable_area: Mapped[float] = mapped_column(Float, default=0.0)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # 关系
    user = relationship("User", back_populates="properties")
    community = relationship("Community")
