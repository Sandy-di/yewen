"""角色变更记录 Schema"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


class RoleLogOut(BaseModel):
    """角色变更记录输出"""
    id: str
    userId: str
    oldRole: str
    newRole: str
    oldRoleLabel: str = ""
    newRoleLabel: str = ""
    reason: str = ""
    operatedBy: Optional[str] = None
    operatorNickname: str = ""
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True
