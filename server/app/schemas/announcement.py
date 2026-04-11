"""公告相关 Schema"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


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
    title: str
    content: str = ""
    type: str = "notice"  # vote / notice / finance
    publisher: str = "物业"
    publisherName: str = ""
    isTop: bool = False
