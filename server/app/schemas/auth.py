"""认证相关 Schema"""

from typing import Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    """微信登录请求"""
    code: str  # wx.login 获取的 code


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    user_id: str
    role: str
    nickname: str
    is_new: bool = False


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
    properties: list = []

    class Config:
        from_attributes = True
