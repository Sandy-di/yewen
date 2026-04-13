"""工单服务 — CRUD + 状态机 + 评价/复修"""

import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RepairOrder, OrderTimeline, User, UserProperty
from app.schemas.order import OrderCreate
from app.utils.logger import get_logger

logger = get_logger("order_service")

# 合法状态流转
VALID_TRANSITIONS = {
    "submitted": ["accepted"],
    "accepted": ["processing"],
    "processing": ["pending_check"],
    "pending_check": ["completed", "rework"],
    "rework": ["processing"],
    "completed": [],
}


class OrderService:
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
    ) -> tuple[list[RepairOrder], int]:
        """获取工单列表"""
        query = select(RepairOrder)
        count_query = select(RepairOrder)

        # 业主只能看自己的工单
        if user.role == "owner":
            query = query.where(RepairOrder.user_id == user.id)
            count_query = count_query.where(RepairOrder.user_id == user.id)
        elif user.community_id:
            query = query.where(RepairOrder.community_id == user.community_id)
            count_query = count_query.where(RepairOrder.community_id == user.community_id)

        if status and status != "all":
            query = query.where(RepairOrder.status == status)
            count_query = count_query.where(RepairOrder.status == status)
        if category:
            query = query.where(RepairOrder.category == category)
            count_query = count_query.where(RepairOrder.category == category)
        if keyword:
            query = query.where(RepairOrder.description.contains(keyword))
            count_query = count_query.where(RepairOrder.description.contains(keyword))

        # 总数
        total_result = await self.db.execute(
            select(func.count()).select_from(count_query.subquery())
        )
        total = total_result.scalar() or 0

        # 分页
        query = query.order_by(RepairOrder.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        items = result.scalars().all()
        return items, total

    async def get_by_id(self, order_id: str) -> RepairOrder | None:
        """获取工单详情"""
        result = await self.db.execute(
            select(RepairOrder).where(RepairOrder.id == order_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user: User, data: OrderCreate) -> RepairOrder:
        """创建报修工单"""
        # 获取用户默认房产
        prop_result = await self.db.execute(
            select(UserProperty).where(
                UserProperty.user_id == user.id,
                UserProperty.is_default == True,
            )
        )
        default_prop = prop_result.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        order = RepairOrder(
            community_id=user.community_id,
            user_id=user.id,
            category=data.category,
            sub_category=data.subCategory,
            description=data.description,
            photos=json.dumps(data.photos),
            status="submitted",
            property_id=default_prop.id if default_prop else None,
            contact_phone=data.contactPhone or user.phone,
            sla_level=24,
            sla_deadline=now + timedelta(hours=24),
        )
        self.db.add(order)
        await self.db.flush()

        # 添加时间线
        timeline = OrderTimeline(
            order_id=order.id,
            content="业主提交报修",
            type="submitted",
        )
        self.db.add(timeline)
        await self.db.flush()

        logger.info(f"工单创建: {order.id}")
        return order

    async def accept(self, order_id: str, user: User) -> RepairOrder:
        """接单（物业）"""
        order = await self.get_by_id(order_id)
        if not order:
            raise ValueError("工单不存在")
        if order.status != "submitted":
            raise ValueError(f"工单状态为{order.status}，无法接单")

        order.status = "accepted"
        order.accepted_at = datetime.now(timezone.utc)
        order.accepted_by = user.id
        self.db.add(order)

        timeline = OrderTimeline(
            order_id=order.id,
            content="物业已接单",
            type="accepted",
        )
        self.db.add(timeline)
        await self.db.flush()
        return order

    async def process(self, order_id: str) -> RepairOrder:
        """开始处理"""
        order = await self.get_by_id(order_id)
        if not order:
            raise ValueError("工单不存在")
        if order.status not in ("accepted", "rework"):
            raise ValueError(f"工单状态为{order.status}，无法开始处理")

        order.status = "processing"
        self.db.add(order)

        timeline = OrderTimeline(
            order_id=order.id,
            content="开始维修处理",
            type="processing",
        )
        self.db.add(timeline)
        await self.db.flush()
        return order

    async def complete(self, order_id: str, note: str = "", completion_photos: list | None = None) -> RepairOrder:
        """完成维修"""
        order = await self.get_by_id(order_id)
        if not order:
            raise ValueError("工单不存在")
        if order.status != "processing":
            raise ValueError(f"工单状态为{order.status}，无法完成")

        order.status = "pending_check"
        order.completed_at = datetime.now(timezone.utc)
        order.completion_note = note
        if completion_photos:
            order.completion_photos = json.dumps(completion_photos)
        self.db.add(order)

        timeline = OrderTimeline(
            order_id=order.id,
            content=f"维修完成{('：' + note) if note else ''}",
            type="completed",
        )
        self.db.add(timeline)
        await self.db.flush()
        return order

    async def rate(self, order_id: str, user: User, rating: int, comment: str = "") -> RepairOrder:
        """评价工单"""
        order = await self.get_by_id(order_id)
        if not order:
            raise ValueError("工单不存在")
        if order.user_id != user.id:
            raise ValueError("只能评价自己的工单")
        if order.status != "pending_check":
            raise ValueError("工单状态不允许评价")

        order.rating = rating
        order.rating_comment = comment
        order.status = "completed"
        self.db.add(order)

        timeline = OrderTimeline(
            order_id=order.id,
            content=f"业主验收通过，评价{rating}星",
            type="verified",
        )
        self.db.add(timeline)
        await self.db.flush()
        return order

    async def rework(self, order_id: str, user: User, reason: str) -> RepairOrder:
        """申请复修"""
        order = await self.get_by_id(order_id)
        if not order:
            raise ValueError("工单不存在")
        if order.user_id != user.id:
            raise ValueError("只能对自己的工单申请复修")
        if order.status != "pending_check":
            raise ValueError("工单状态不允许复修")

        order.status = "rework"
        self.db.add(order)

        timeline = OrderTimeline(
            order_id=order.id,
            content=f"业主申请复修：{reason}",
            type="rework",
        )
        self.db.add(timeline)
        await self.db.flush()
        return order

    def get_property_name(self, order: RepairOrder) -> str:
        """获取工单关联的房产名称（需在已有session上下文中使用）"""
        if order.property_ref:
            p = order.property_ref
            return f"{p.building}{p.unit}{p.room_no}"
        return ""
