"""用户相关 Schema"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class UserUpdate(BaseModel):
    """更新用户信息"""
    nickname: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    avatar: Optional[str] = Field(None, max_length=500)


class UserListOut(BaseModel):
    """用户列表项（管理端）"""
    id: str
    nickname: str = ""
    phone: str = ""
    avatar: str = ""
    role: str = "owner"
    verifiedLevel: int = 0
    communityId: Optional[str] = None
    isActive: bool = True
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


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
    level: int = Field(..., ge=1, le=4, description="核验等级 1-4")
    data: dict = {}


class VerifyResponse(BaseModel):
    """身份核验响应"""
    success: bool
    verifiedLevel: int


class UserRoleUpdate(BaseModel):
    """修改用户角色 — 支持中文输入"""
    role: str = Field(..., min_length=1, max_length=20, description="角色（中文或英文均可：业主/owner, 物业/property, 业委会/committee）")
    reason: str = Field("", max_length=500, description="变更原因")


class UserActiveUpdate(BaseModel):
    """修改用户状态"""
    isActive: bool
