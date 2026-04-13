"""工单相关 Schema"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


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
    video: str = ""
    appointmentTime: str = ""
    completedAt: Optional[datetime] = None
    completionPhotos: list = []
    completionNote: str = ""
    rating: Optional[int] = None
    ratingComment: str = ""
    slaLevel: int = 24


class OrderCreate(BaseModel):
    """创建报修"""
    category: str = Field(..., min_length=1, max_length=30, description="工单分类")
    subCategory: str = Field("", max_length=50)
    description: str = Field(..., min_length=1, max_length=2000)
    photos: list = []
    video: str = Field("", max_length=500, description="视频URL")
    appointmentTime: str = Field("", max_length=30, description="预约上门时间")
    contactPhone: str = Field("", max_length=20)


class OrderCreateResponse(BaseModel):
    success: bool
    orderId: Optional[str] = None


class RateRequest(BaseModel):
    """评价请求"""
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field("", max_length=500)


class ReworkRequest(BaseModel):
    """复修请求"""
    reason: str = Field(..., min_length=1, max_length=500)


class CompleteRequest(BaseModel):
    """完成维修请求"""
    note: str = Field("", max_length=500)
    completionPhotos: list = []
