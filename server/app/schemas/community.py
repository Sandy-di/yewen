"""社区相关 Schema"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class CommunityOut(BaseModel):
    """社区信息输出"""
    id: str
    name: str
    totalUnits: int = 0
    totalArea: float = 0.0
    address: str = ""
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class CommunityCreate(BaseModel):
    """创建社区"""
    name: str = Field(..., min_length=1, max_length=100)
    totalUnits: int = Field(0, ge=0)
    totalArea: float = Field(0.0, ge=0)
    address: str = Field("", max_length=255)


class CommunityUpdate(BaseModel):
    """更新社区"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    totalUnits: Optional[int] = Field(None, ge=0)
    totalArea: Optional[float] = Field(None, ge=0)
    address: Optional[str] = Field(None, max_length=255)
