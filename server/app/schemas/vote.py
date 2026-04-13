"""投票相关 Schema"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class VoteOptionOut(BaseModel):
    id: str
    label: str
    count: int
    area: float

    class Config:
        from_attributes = True


class VoteOptionCreate(BaseModel):
    label: str = Field(..., min_length=1, max_length=100)


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
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field("", max_length=5000)
    verificationLevel: int = Field(1, ge=1, le=4)
    voteType: str = Field("double_majority", pattern="^(double_majority|double_three_quarters|simple)$")
    startTime: Optional[datetime] = None
    endTime: Optional[datetime] = None
    options: List[VoteOptionCreate] = Field(..., min_length=2)


class VoteSubmit(BaseModel):
    """提交投票"""
    optionId: str = Field(..., min_length=1)


class VoteSubmitResponse(BaseModel):
    success: bool
    txHash: Optional[str] = None


class VoteCreateResponse(BaseModel):
    success: bool
    voteId: Optional[str] = None
