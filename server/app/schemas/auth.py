"""认证相关 Schema"""

from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """微信登录请求"""
    code: str = Field(..., min_length=1, max_length=100, description="wx.login 获取的 code")


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    user_id: str
    role: str
    nickname: str
    is_new: bool = False


class IdentitiesInfo(BaseModel):
    """用户身份信息（叠加关系）"""
    isOwner: bool = False
    isProperty: bool = False
    isCommittee: bool = False


class ProfileResponse(BaseModel):
    """用户资料响应"""
    userId: str
    openid: str
    nickname: str
    phone: str
    avatar: str
    role: str
    verifiedLevel: int
    communityId: Optional[str] = None
    communityName: Optional[str] = None
    identities: IdentitiesInfo = IdentitiesInfo()
    properties: list = []

    class Config:
        from_attributes = True
