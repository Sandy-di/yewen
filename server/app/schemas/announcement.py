"""公告相关 Schema"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class AnnouncementListOut(BaseModel):
    """公告列表项"""
    id: str
    title: str
    type: str
    publisher: str
    publisherName: str
    isTop: bool
    readCount: int = 0
    totalUsers: int = 0
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class AnnouncementDetailOut(AnnouncementListOut):
    """公告详情"""
    content: str


class AnnouncementCreate(BaseModel):
    """创建公告"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field("", max_length=10000)
    type: str = Field("notice", pattern="^(vote|notice|finance)$")
    publisher: str = Field("物业", max_length=20)
    publisherName: str = Field("", max_length=50)
    isTop: bool = False


class AnnouncementUpdate(BaseModel):
    """编辑公告"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, max_length=10000)
    type: Optional[str] = Field(None, pattern="^(vote|notice|finance)$")
    isTop: Optional[bool] = None
