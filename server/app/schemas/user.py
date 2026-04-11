"""用户相关 Schema"""

from typing import Optional
from pydantic import BaseModel


class UserUpdate(BaseModel):
    """更新用户信息"""
    nickname: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None


class PropertyOut(BaseModel):
    """房产信息输出"""
    propertyId: str
    building: str
    unit: str
    roomNo: str
    usableArea: float
    isDefault: bool

    class Config:
        from_attributes = True


class VerifyRequest(BaseModel):
    """身份核验请求"""
    level: int  # 1-4
    data: dict = {}


class VerifyResponse(BaseModel):
    """身份核验响应"""
    success: bool
    verifiedLevel: int
