"""社区管理服务 — CRUD"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Community
from app.schemas.community import CommunityCreate, CommunityUpdate
from app.utils.logger import get_logger

logger = get_logger("community_service")


class CommunityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self, *, page: int = 1, page_size: int = 20
    ) -> tuple[list[Community], int]:
        """获取社区列表"""
        total_result = await self.db.execute(
            select(func.count(Community.id))
        )
        total = total_result.scalar() or 0

        query = select(Community).order_by(Community.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        items = result.scalars().all()
        return items, total

    async def get_by_id(self, community_id: str) -> Community | None:
        """获取社区详情"""
        result = await self.db.execute(
            select(Community).where(Community.id == community_id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: CommunityCreate) -> Community:
        """创建社区 — 同名校验"""
        # 同名校验
        existing = await self.db.execute(
            select(Community).where(Community.name == data.name.strip())
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"社区名称「{data.name}」已存在，请使用其他名称")

        community = Community(
            name=data.name,
            total_units=data.totalUnits,
            total_area=data.totalArea,
            address=data.address,
        )
        self.db.add(community)
        await self.db.flush()
        logger.info(f"社区创建: {community.id} - {community.name}")
        return community

    async def update(self, community_id: str, data: CommunityUpdate) -> Community | None:
        """更新社区信息"""
        community = await self.get_by_id(community_id)
        if not community:
            return None

        if data.name is not None:
            # 同名校验（排除自身）
            existing = await self.db.execute(
                select(Community).where(Community.name == data.name.strip(), Community.id != community_id)
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"社区名称「{data.name}」已存在，请使用其他名称")
            community.name = data.name
        if data.totalUnits is not None:
            community.total_units = data.totalUnits
        if data.totalArea is not None:
            community.total_area = data.totalArea
        if data.address is not None:
            community.address = data.address

        self.db.add(community)
        await self.db.flush()
        return community
