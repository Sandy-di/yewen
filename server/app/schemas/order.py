"""工单相关 Schema"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class TimelineOut(BaseModel):
    time: str
    content: str
    type: str

    class Config:
        from_attributes = True


class OrderListOut(BaseModel):
    """工单列表项"""
    orderId: str
    category: str
    subCategory: str
    description: str
    status: str
    contactPhone: str = ""
    createdAt: Optional[datetime] = None
    acceptedAt: Optional[datetime] = None
    acceptedBy: Optional[str] = None
    acceptorPhone: str = ""
    estimatedTime: str = ""
    slaDeadline: Optional[datetime] = None
    timeline: List[TimelineOut] = []

    class Config:
        from_attributes = True


class OrderDetailOut(OrderListOut):
    """工单详情"""
    propertyId: Optional[str] = None
    propertyName: str = ""
    photos: list = []
    completedAt: Optional[datetime] = None
    completionPhotos: list = []
    completionNote: str = ""
    rating: Optional[int] = None
    ratingComment: str = ""
    slaLevel: int = 24


class OrderCreate(BaseModel):
    """创建报修"""
    category: str
    subCategory: str = ""
    description: str
    photos: list = []
    contactPhone: str = ""


class OrderCreateResponse(BaseModel):
    success: bool
    orderId: Optional[str] = None


class RateRequest(BaseModel):
    """评价请求"""
    rating: int
    comment: str = ""


class ReworkRequest(BaseModel):
    """复修请求"""
    reason: str
