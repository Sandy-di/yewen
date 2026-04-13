"""数据统计/仪表盘路由"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.middleware.auth import get_current_user
from app.services.stats_service import StatsService

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取仪表盘统计数据"""
    service = StatsService(db)
    stats = await service.get_dashboard(current_user)
    return stats


@router.get("/overview")
async def get_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取社区概览数据（业主数、工单数、投票数等）"""
    service = StatsService(db)
    overview = await service.get_overview(current_user)
    return overview
