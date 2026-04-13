"""数据统计 Schema"""

from typing import Optional
from pydantic import BaseModel


class DashboardStats(BaseModel):
    """仪表盘统计"""
    totalUsers: int = 0
    totalVotes: int = 0
    activeVotes: int = 0
    totalOrders: int = 0
    pendingOrders: int = 0
    processingOrders: int = 0
    totalFinance: int = 0
    pendingFinance: int = 0
    totalAnnouncements: int = 0


class OverviewStats(BaseModel):
    """社区概览"""
    communityName: str = ""
    totalUnits: int = 0
    totalArea: float = 0.0
    totalOwners: int = 0
    recentOrders: int = 0
    activeVotes: int = 0
