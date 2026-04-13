"""投诉相关 Schema"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ComplaintReplyOut(BaseModel):
    """投诉回复项"""
    id: str
    userId: str
    content: str
    replyType: str  # reply/supervise/resolve
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class ComplaintListOut(BaseModel):
    """投诉列表项"""
    complaintId: str
    title: str
    category: str
    status: str
    isImportant: bool = False
    slaDeadline: Optional[datetime] = None
    createdAt: Optional[datetime] = None
    replyCount: int = 0

    class Config:
        from_attributes = True


class ComplaintDetailOut(ComplaintListOut):
    """投诉详情"""
    content: str = ""
    photos: list = []
    userId: str = ""
    resolvedAt: Optional[datetime] = None
    replies: List[ComplaintReplyOut] = []


class ComplaintCreate(BaseModel):
    """创建投诉"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1, max_length=5000)
    category: str = Field("other", max_length=30)
    photos: list = []


class ComplaintReplyCreate(BaseModel):
    """回复投诉"""
    content: str = Field(..., min_length=1, max_length=2000)
    replyType: str = Field("reply", pattern="^(reply|supervise|resolve)$")


class ComplaintCreateResponse(BaseModel):
    success: bool
    complaintId: Optional[str] = None


class ComplaintMarkImportant(BaseModel):
    """标记重要"""
    isImportant: bool
