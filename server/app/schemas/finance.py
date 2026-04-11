"""财务相关 Schema"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class FinanceItemOut(BaseModel):
    itemType: str
    category: str
    amount: float
    description: str

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


class FinanceItemCreate(BaseModel):
    itemType: str  # income / expense
    category: str
    amount: float
    description: str = ""


class FinanceCreate(BaseModel):
    """创建财务报表"""
    month: str
    title: str
    items: List[FinanceItemCreate] = []
