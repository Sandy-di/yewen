"""投票相关 Schema"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class VoteOptionOut(BaseModel):
    id: str
    label: str
    count: int
    area: float

    class Config:
        from_attributes = True


class VoteOptionCreate(BaseModel):
    label: str


class VoteListOut(BaseModel):
    """投票列表项"""
    voteId: str
    title: str
    status: str
    voteType: str
    verificationLevel: int
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    totalProperties: int
    participatedCount: int
    participatedArea: float
    totalArea: float
    options: List[VoteOptionOut] = []
    createdBy: Optional[str] = None
    createdAt: Optional[datetime] = None
    result: Optional[str] = None
    resultSummary: Optional[str] = None

    class Config:
        from_attributes = True


class VoteDetailOut(VoteListOut):
    """投票详情"""
    description: str = ""
    resultHash: Optional[str] = None


class VoteCreate(BaseModel):
    """创建投票"""
    title: str
    description: str = ""
    verificationLevel: int = 1
    voteType: str = "double_majority"
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    options: List[VoteOptionCreate] = []


class VoteSubmit(BaseModel):
    """提交投票"""
    optionId: str


class VoteSubmitResponse(BaseModel):
    success: bool
    txHash: Optional[str] = None


class VoteCreateResponse(BaseModel):
    success: bool
    voteId: Optional[str] = None
