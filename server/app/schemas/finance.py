"""财务相关 Schema"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class FinanceAttachmentOut(BaseModel):
    """附件输出"""
    name: str
    url: str
    size: int = 0  # bytes


class FinanceItemOut(BaseModel):
    itemType: str
    category: str
    amount: float
    description: str
    receiptUrl: str = ""  # 凭证URL

    class Config:
        from_attributes = True


class FinanceQuestionOut(BaseModel):
    """业主提问输出"""
    id: str
    itemId: Optional[str] = None
    userId: str
    question: str
    answer: str = ""
    answeredBy: Optional[str] = None
    answeredAt: Optional[datetime] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class FinanceListOut(BaseModel):
    """财务列表项"""
    reportId: str
    month: str
    title: str
    status: str
    submittedBy: Optional[str] = None
    submittedAt: Optional[datetime] = None
    approvedBy: Optional[str] = None
    approvedAt: Optional[datetime] = None
    totalIncome: float = 0
    totalExpense: float = 0
    balance: float = 0

    class Config:
        from_attributes = True


class FinanceDetailOut(FinanceListOut):
    """财务详情"""
    items: List[FinanceItemOut] = []
    attachments: List[FinanceAttachmentOut] = []
    questions: List[FinanceQuestionOut] = []


class FinanceItemCreate(BaseModel):
    itemType: str = Field(..., pattern="^(income|expense)$")
    category: str = Field(..., min_length=1, max_length=50)
    amount: float = Field(..., gt=0)
    description: str = Field("", max_length=200)
    receiptUrl: str = Field("", max_length=500, description="凭证URL")


class FinanceCreate(BaseModel):
    """创建财务报表"""
    month: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="月份，格式 2026-03")
    title: str = Field(..., min_length=1, max_length=200)
    items: List[FinanceItemCreate] = Field(..., min_length=1)
    attachments: List[FinanceAttachmentOut] = Field([], description="附件列表")


class FinanceRejectRequest(BaseModel):
    """拒绝财务报表"""
    reason: str = Field("", max_length=500)


class FinanceQuestionCreate(BaseModel):
    """业主提问"""
    question: str = Field(..., min_length=1, max_length=1000)
    itemId: Optional[str] = None


class FinanceQuestionAnswer(BaseModel):
    """物业回答提问"""
    answer: str = Field(..., min_length=1, max_length=2000)
