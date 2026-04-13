"""投诉服务 — CRUD + 回复 + 标记重要 + SLA"""

import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Complaint, ComplaintReply, User
from app.schemas.complaint import ComplaintCreate
from app.utils.logger import get_logger

logger = get_logger("complaint_service")


class ComplaintService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        user: User,
        *,
        status: str | None = None,
        category: str | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Complaint], int]:
        """获取投诉列表"""
        query = select(Complaint)
        count_query = select(Complaint)

        # 业主只能看自己的投诉
        if user.role == "owner":
            query = query.where(Complaint.user_id == user.id)
            count_query = count_query.where(Complaint.user_id == user.id)
        elif user.community_id:
            query = query.where(Complaint.community_id == user.community_id)
            count_query = count_query.where(Complaint.community_id == user.community_id)

        if status and status != "all":
            query = query.where(Complaint.status == status)
            count_query = count_query.where(Complaint.status == status)
        if category:
            query = query.where(Complaint.category == category)
            count_query = count_query.where(Complaint.category == category)
        if keyword:
            query = query.where(Complaint.title.contains(keyword))
            count_query = count_query.where(Complaint.title.contains(keyword))

        # 总数
        total_result = await self.db.execute(
            select(func.count()).select_from(count_query.subquery())
        )
        total = total_result.scalar() or 0

        # 分页
        query = query.order_by(Complaint.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        items = result.scalars().all()
        return items, total

    async def get_by_id(self, complaint_id: str) -> Complaint | None:
        """获取投诉详情"""
        result = await self.db.execute(
            select(Complaint).where(Complaint.id == complaint_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user: User, data: ComplaintCreate) -> Complaint:
        """创建投诉"""
        now = datetime.now(timezone.utc)
        complaint = Complaint(
            community_id=user.community_id,
            user_id=user.id,
            title=data.title,
            content=data.content,
            category=data.category,
            photos=json.dumps(data.photos),
            status="submitted",
            sla_deadline=now + timedelta(hours=48),
        )
        self.db.add(complaint)
        await self.db.flush()

        logger.info(f"投诉创建: {complaint.id}")
        return complaint

    async def reply(
        self, complaint_id: str, user: User, content: str, reply_type: str = "reply"
    ) -> ComplaintReply:
        """回复投诉"""
        complaint = await self.get_by_id(complaint_id)
        if not complaint:
            raise ValueError("投诉不存在")

        reply = ComplaintReply(
            complaint_id=complaint_id,
            user_id=user.id,
            content=content,
            reply_type=reply_type,
        )
        self.db.add(reply)

        # 更新投诉状态
        if reply_type == "resolve":
            complaint.status = "resolved"
            complaint.resolved_at = datetime.now(timezone.utc)
        elif complaint.status == "submitted":
            complaint.status = "replied"

        self.db.add(complaint)
        await self.db.flush()

        logger.info(f"投诉回复: {complaint_id}, type={reply_type}")
        return reply

    async def mark_important(self, complaint_id: str, is_important: bool) -> None:
        """标记投诉为重要（业委会操作）"""
        complaint = await self.get_by_id(complaint_id)
        if not complaint:
            raise ValueError("投诉不存在")
        complaint.is_important = is_important
        self.db.add(complaint)
        await self.db.flush()

    async def close(self, complaint_id: str) -> None:
        """关闭投诉"""
        complaint = await self.get_by_id(complaint_id)
        if not complaint:
            raise ValueError("投诉不存在")
        complaint.status = "closed"
        self.db.add(complaint)
        await self.db.flush()
