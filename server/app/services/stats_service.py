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

    async def get_sla_dashboard(self, user: User) -> dict:
        """SLA监控看板：按时完成率、平均响应时长、好评率、分类统计"""
        community_id = user.community_id
        if not community_id:
            return {
                "onTimeRate": 0, "avgResponseMinutes": 0, "avgCompleteHours": 0,
                "goodRate": 0, "byCategory": [], "byAcceptor": [],
                "slaBreached": 0, "totalCompleted": 0,
            }

        from datetime import datetime, timedelta, timezone

        # 已完成的工单（用于计算各项指标）
        base_query = select(RepairOrder).where(
            RepairOrder.community_id == community_id,
            RepairOrder.status == "completed",
        )
        result = await self.db.execute(base_query)
        completed_orders = result.scalars().all()

        total_completed = len(completed_orders)
        if total_completed == 0:
            return {
                "onTimeRate": 0, "avgResponseMinutes": 0, "avgCompleteHours": 0,
                "goodRate": 0, "byCategory": [], "byAcceptor": [],
                "slaBreached": 0, "totalCompleted": 0,
            }

        # 按时完成率
        on_time_count = 0
        sla_breached = 0
        total_response_minutes = 0
        total_complete_hours = 0
        good_count = 0
        response_count = 0
        category_stats: dict[str, dict] = {}
        acceptor_stats: dict[str, dict] = {}

        for o in completed_orders:
            # SLA按时
            if o.sla_deadline and o.completed_at:
                if o.completed_at <= o.sla_deadline:
                    on_time_count += 1
                else:
                    sla_breached += 1

            # 响应时长（提交→接单）
            if o.accepted_at and o.created_at:
                delta = (o.accepted_at - o.created_at).total_seconds() / 60
                total_response_minutes += delta
                response_count += 1

            # 完成时长（提交→完成）
            if o.completed_at and o.created_at:
                delta = (o.completed_at - o.created_at).total_seconds() / 3600
                total_complete_hours += delta

            # 好评（4-5星）
            if o.rating and o.rating >= 4:
                good_count += 1

            # 分类统计
            cat = o.category or "other"
            if cat not in category_stats:
                category_stats[cat] = {"total": 0, "onTime": 0, "good": 0}
            category_stats[cat]["total"] += 1
            if o.sla_deadline and o.completed_at and o.completed_at <= o.sla_deadline:
                category_stats[cat]["onTime"] += 1
            if o.rating and o.rating >= 4:
                category_stats[cat]["good"] += 1

            # 接单人统计
            acc = o.accepted_by or "unassigned"
            if acc not in acceptor_stats:
                acceptor_stats[acc] = {"total": 0, "onTime": 0, "good": 0, "avgHours": 0, "totalHours": 0}
            acceptor_stats[acc]["total"] += 1
            if o.sla_deadline and o.completed_at and o.completed_at <= o.sla_deadline:
                acceptor_stats[acc]["onTime"] += 1
            if o.rating and o.rating >= 4:
                acceptor_stats[acc]["good"] += 1
            if o.completed_at and o.created_at:
                acceptor_stats[acc]["totalHours"] += (o.completed_at - o.created_at).total_seconds() / 3600

        # 汇总接单人平均时长
        by_acceptor = []
        for acc_id, stats in acceptor_stats.items():
            by_acceptor.append({
                "acceptorId": acc_id,
                "total": stats["total"],
                "onTimeRate": round(stats["onTime"] / stats["total"] * 100, 1) if stats["total"] else 0,
                "goodRate": round(stats["good"] / stats["total"] * 100, 1) if stats["total"] else 0,
                "avgHours": round(stats["totalHours"] / stats["total"], 1) if stats["total"] else 0,
            })

        by_category = []
        for cat, stats in category_stats.items():
            by_category.append({
                "category": cat,
                "total": stats["total"],
                "onTimeRate": round(stats["onTime"] / stats["total"] * 100, 1) if stats["total"] else 0,
                "goodRate": round(stats["good"] / stats["total"] * 100, 1) if stats["total"] else 0,
            })

        return {
            "onTimeRate": round(on_time_count / total_completed * 100, 1),
            "avgResponseMinutes": round(total_response_minutes / response_count, 1) if response_count else 0,
            "avgCompleteHours": round(total_complete_hours / total_completed, 1),
            "goodRate": round(good_count / total_completed * 100, 1),
            "byCategory": by_category,
            "byAcceptor": by_acceptor,
            "slaBreached": sla_breached,
            "totalCompleted": total_completed,
        }
