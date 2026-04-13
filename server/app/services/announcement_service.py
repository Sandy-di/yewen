"""公告服务 — CRUD + 阅读统计"""

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Announcement, AnnouncementRead, User, Community
from app.schemas.announcement import AnnouncementCreate, AnnouncementUpdate
from app.utils.logger import get_logger

logger = get_logger("announcement_service")


class AnnouncementService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        community_id: str | None,
        *,
        type_: str | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        """
        获取公告列表（含阅读数统计）
        返回 [(announcement, read_count, total_users), ...], total
        """
        query = select(Announcement)
        count_query = select(Announcement)

        if community_id:
            query = query.where(Announcement.community_id == community_id)
            count_query = count_query.where(Announcement.community_id == community_id)

        if type_ and type_ != "all":
            query = query.where(Announcement.type == type_)
            count_query = count_query.where(Announcement.type == type_)
        if keyword:
            query = query.where(Announcement.title.contains(keyword))
            count_query = count_query.where(Announcement.title.contains(keyword))

        # 总数
        total_result = await self.db.execute(
            select(func.count()).select_from(count_query.subquery())
        )
        total = total_result.scalar() or 0

        # 分页 — 置顶优先，然后按时间倒序
        query = query.order_by(Announcement.is_top.desc(), Announcement.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        announcements = result.scalars().all()

        # 获取社区总人数
        total_users = 0
        if community_id:
            user_count_result = await self.db.execute(
                select(func.count(User.id)).where(User.community_id == community_id)
            )
            total_users = user_count_result.scalar() or 0

        # 批量获取阅读数（修复N+1查询）
        ann_ids = [ann.id for ann in announcements]
        read_counts = {}
        if ann_ids:
            read_result = await self.db.execute(
                select(
                    AnnouncementRead.announcement_id,
                    func.count(AnnouncementRead.id),
                )
                .where(AnnouncementRead.announcement_id.in_(ann_ids))
                .group_by(AnnouncementRead.announcement_id)
            )
            read_counts = dict(read_result.all())

        items = [
            {
                "announcement": ann,
                "read_count": read_counts.get(ann.id, 0),
                "total_users": total_users,
            }
            for ann in announcements
        ]
        return items, total

    async def get_by_id(self, ann_id: str, user: User) -> dict | None:
        """获取公告详情（自动记录阅读）"""
        result = await self.db.execute(
            select(Announcement).where(Announcement.id == ann_id)
        )
        ann = result.scalar_one_or_none()
        if not ann:
            return None

        # 记录阅读
        exist = await self.db.execute(
            select(AnnouncementRead).where(
                AnnouncementRead.announcement_id == ann_id,
                AnnouncementRead.user_id == user.id,
            )
        )
        if not exist.scalar_one_or_none():
            read_record = AnnouncementRead(
                announcement_id=ann_id,
                user_id=user.id,
            )
            self.db.add(read_record)
            await self.db.flush()

        # 获取阅读数
        read_result = await self.db.execute(
            select(func.count(AnnouncementRead.id)).where(
                AnnouncementRead.announcement_id == ann_id
            )
        )
        read_count = read_result.scalar() or 0

        total_users = 0
        if ann.community_id:
            user_count_result = await self.db.execute(
                select(func.count(User.id)).where(User.community_id == ann.community_id)
            )
            total_users = user_count_result.scalar() or 0

        return {
            "announcement": ann,
            "read_count": read_count,
            "total_users": total_users,
        }

    async def create(self, user: User, data: AnnouncementCreate) -> Announcement:
        """发布公告"""
        ann = Announcement(
            community_id=user.community_id,
            title=data.title,
            content=data.content,
            type=data.type,
            publisher=data.publisher,
            publisher_name=data.publisherName or user.nickname,
            is_top=data.isTop,
            created_by=user.id,
        )
        self.db.add(ann)
        await self.db.flush()
        logger.info(f"公告创建: {ann.id} - {ann.title}")
        return ann

    async def update(self, ann_id: str, data: AnnouncementUpdate) -> Announcement | None:
        """编辑公告"""
        result = await self.db.execute(
            select(Announcement).where(Announcement.id == ann_id)
        )
        ann = result.scalar_one_or_none()
        if not ann:
            return None

        if data.title is not None:
            ann.title = data.title
        if data.content is not None:
            ann.content = data.content
        if data.type is not None:
            ann.type = data.type
        if data.isTop is not None:
            ann.is_top = data.isTop

        self.db.add(ann)
        await self.db.flush()
        logger.info(f"公告编辑: {ann.id}")
        return ann

    async def delete(self, ann_id: str) -> bool:
        """删除公告"""
        result = await self.db.execute(
            select(Announcement).where(Announcement.id == ann_id)
        )
        ann = result.scalar_one_or_none()
        if not ann:
            return False

        # 先删除阅读记录
        await self.db.execute(
            delete(AnnouncementRead).where(AnnouncementRead.announcement_id == ann_id)
        )
        await self.db.delete(ann)
        await self.db.flush()
        logger.info(f"公告删除: {ann_id}")
        return True
