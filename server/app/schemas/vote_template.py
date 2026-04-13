"""投票模板 Schema"""

from typing import Optional, List
from pydantic import BaseModel


class VoteTemplateOut(BaseModel):
    """投票模板输出"""
    id: str
    name: str
    description: str = ""
    voteType: str
    verificationLevel: int
    optionsTemplate: list = []
    descriptionTemplate: str = ""
    sortOrder: int = 0

    class Config:
        from_attributes = True
