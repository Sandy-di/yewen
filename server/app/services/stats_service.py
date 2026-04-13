"""数据统计服务 — 仪表盘 + 社区概览"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Vote, RepairOrder, FinanceReport, Announcement, Community
from app.utils.logger import get_logger

logger = get_logger("stats_service")


class StatsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self, user: User) -> dict:
        """获取仪表盘统计数据"""
        community_id = user.community_id

        # 基础过滤
        community_filter = {}
        if community_id:
            community_filter = {"community_id": community_id}

        # 用户数
        user_query = select(func.count(User.id))
        if community_id:
            user_query = user_query.where(User.community_id == community_id)
        total_users = (await self.db.execute(user_query)).scalar() or 0

        # 投票数
        vote_query = select(func.count(Vote.id))
        if community_id:
            vote_query = vote_query.where(Vote.community_id == community_id)
        total_votes = (await self.db.execute(vote_query)).scalar() or 0

        active_vote_query = select(func.count(Vote.id)).where(Vote.status == "active")
        if community_id:
            active_vote_query = active_vote_query.where(Vote.community_id == community_id)
        active_votes = (await self.db.execute(active_vote_query)).scalar() or 0

        # 工单数
        order_query = select(func.count(RepairOrder.id))
        if community_id:
            order_query = order_query.where(RepairOrder.community_id == community_id)
        total_orders = (await self.db.execute(order_query)).scalar() or 0

        pending_query = select(func.count(RepairOrder.id)).where(RepairOrder.status == "submitted")
        if community_id:
            pending_query = pending_query.where(RepairOrder.community_id == community_id)
        pending_orders = (await self.db.execute(pending_query)).scalar() or 0

        processing_query = select(func.count(RepairOrder.id)).where(
            RepairOrder.status.in_(["accepted", "processing"])
        )
        if community_id:
            processing_query = processing_query.where(RepairOrder.community_id == community_id)
        processing_orders = (await self.db.execute(processing_query)).scalar() or 0

        # 财务
        finance_query = select(func.count(FinanceReport.id))
        if community_id:
            finance_query = finance_query.where(FinanceReport.community_id == community_id)
        total_finance = (await self.db.execute(finance_query)).scalar() or 0

        pending_finance_query = select(func.count(FinanceReport.id)).where(
            FinanceReport.status == "pending"
        )
        if community_id:
            pending_finance_query = pending_finance_query.where(
                FinanceReport.community_id == community_id
            )
        pending_finance = (await self.db.execute(pending_finance_query)).scalar() or 0

        # 公告数
        ann_query = select(func.count(Announcement.id))
        if community_id:
            ann_query = ann_query.where(Announcement.community_id == community_id)
        total_announcements = (await self.db.execute(ann_query)).scalar() or 0

        return {
            "totalUsers": total_users,
            "totalVotes": total_votes,
            "activeVotes": active_votes,
            "totalOrders": total_orders,
            "pendingOrders": pending_orders,
            "processingOrders": processing_orders,
            "totalFinance": total_finance,
            "pendingFinance": pending_finance,
            "totalAnnouncements": total_announcements,
        }

    async def get_overview(self, user: User) -> dict:
        """获取社区概览"""
        community = None
        if user.community_id:
            result = await self.db.execute(
                select(Community).where(Community.id == user.community_id)
            )
            community = result.scalar_one_or_none()

        if not community:
            return {
                "communityName": "",
                "totalUnits": 0,
                "totalArea": 0.0,
                "totalOwners": 0,
                "recentOrders": 0,
                "activeVotes": 0,
            }

        # 业主数
        owner_count = (
            await self.db.execute(
                select(func.count(User.id)).where(
                    User.community_id == community.id, User.role == "owner"
                )
            )
        ).scalar() or 0

        # 近7天工单数
        from datetime import datetime, timedelta, timezone
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_orders = (
            await self.db.execute(
                select(func.count(RepairOrder.id)).where(
                    RepairOrder.community_id == community.id,
                    RepairOrder.created_at >= week_ago,
                )
            )
        ).scalar() or 0

        # 进行中的投票
        active_votes = (
            await self.db.execute(
                select(func.count(Vote.id)).where(
                    Vote.community_id == community.id, Vote.status == "active"
                )
            )
        ).scalar() or 0

        return {
            "communityName": community.name,
            "totalUnits": community.total_units,
            "totalArea": community.total_area,
            "totalOwners": owner_count,
            "recentOrders": recent_orders,
            "activeVotes": active_votes,
        }
