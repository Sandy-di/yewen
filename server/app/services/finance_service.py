"""财务服务 — CRUD + 审批"""

from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FinanceReport, FinanceItem, User
from app.schemas.finance import FinanceCreate
from app.utils.logger import get_logger

logger = get_logger("finance_service")


class FinanceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        community_id: str | None,
        *,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[FinanceReport], int]:
        """获取财务报表列表"""
        query = select(FinanceReport)
        count_query = select(FinanceReport)

        if community_id:
            query = query.where(FinanceReport.community_id == community_id)
            count_query = count_query.where(FinanceReport.community_id == community_id)

        if status and status != "all":
            query = query.where(FinanceReport.status == status)
            count_query = count_query.where(FinanceReport.status == status)

        # 总数
        total_result = await self.db.execute(
            select(func.count()).select_from(count_query.subquery())
        )
        total = total_result.scalar() or 0

        # 分页
        query = query.order_by(FinanceReport.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        items = result.scalars().all()
        return items, total

    async def get_by_id(self, report_id: str) -> FinanceReport | None:
        """获取报表详情"""
        result = await self.db.execute(
            select(FinanceReport).where(FinanceReport.id == report_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user: User, data: FinanceCreate) -> FinanceReport:
        """上报财务报表"""
        now = datetime.now(timezone.utc)

        total_income = sum(i.amount for i in data.items if i.itemType == "income")
        total_expense = sum(i.amount for i in data.items if i.itemType == "expense")
        balance = total_income - total_expense

        # 附件列表
        attachments_json = [
            {"name": a.name, "url": a.url, "size": a.size}
            for a in (data.attachments or [])
        ]

        report = FinanceReport(
            community_id=user.community_id,
            month=data.month,
            title=data.title,
            status="pending",
            submitted_by=user.id,
            submitted_at=now,
            total_income=total_income,
            total_expense=total_expense,
            balance=balance,
        )
        report.set_attachments(attachments_json)
        self.db.add(report)
        await self.db.flush()

        for item in data.items:
            fi = FinanceItem(
                report_id=report.id,
                item_type=item.itemType,
                category=item.category,
                amount=item.amount,
                description=item.description,
                receipt_url=item.receiptUrl or "",
            )
            self.db.add(fi)

        await self.db.flush()
        logger.info(f"财务报表创建: {report.id}")
        return report

    async def approve(self, report_id: str, user: User) -> FinanceReport:
        """审批财务报表"""
        report = await self.get_by_id(report_id)
        if not report:
            raise ValueError("报表不存在")
        if report.status != "pending":
            raise ValueError("报表已审批")

        report.status = "published"
        report.approved_by = user.id
        report.approved_at = datetime.now(timezone.utc)

        # 重新计算汇总（确保一致性）
        total_income = sum(float(i.amount or 0) for i in report.items if i.item_type == "income")
        total_expense = sum(float(i.amount or 0) for i in report.items if i.item_type == "expense")
        report.total_income = total_income
        report.total_expense = total_expense
        report.balance = total_income - total_expense

        self.db.add(report)
        await self.db.flush()
        logger.info(f"财务报表审批通过: {report.id}")
        return report

    async def reject(self, report_id: str, user: User, reason: str = "") -> FinanceReport:
        """拒绝/退回财务报表"""
        report = await self.get_by_id(report_id)
        if not report:
            raise ValueError("报表不存在")
        if report.status != "pending":
            raise ValueError("报表已审批，无法退回")

        report.status = "rejected"
        report.approved_by = user.id
        report.approved_at = datetime.now(timezone.utc)

        self.db.add(report)
        await self.db.flush()
        logger.info(f"财务报表退回: {report.id}, 原因: {reason}")
        return report
