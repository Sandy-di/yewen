"""档案服务 — CRUD + 权限过滤 + 标签检索"""

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Archive, User
from app.schemas.archive import ArchiveCreate
from app.utils.logger import get_logger

logger = get_logger("archive_service")

# 权限等级：业主只能看 public，物业可看 public+internal，业委会可看全部
ACCESS_LEVELS = {
    "owner": ["public"],
    "property": ["public", "internal"],
    "committee": ["public", "internal", "confidential"],
}


class ArchiveService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self, user: User, *,
        category: str | None = None,
        keyword: str | None = None,
        tag: str | None = None,
        page: int = 1, page_size: int = 20,
    ):
        query = select(Archive).where(Archive.community_id == user.community_id)
        count_query = select(func.count(Archive.id)).where(Archive.community_id == user.community_id)

        # 权限过滤
        allowed_levels = ACCESS_LEVELS.get(user.role, ["public"])
        query = query.where(Archive.access_level.in_(allowed_levels))
        count_query = count_query.where(Archive.access_level.in_(allowed_levels))

        if category:
            query = query.where(Archive.category == category)
            count_query = count_query.where(Archive.category == category)
        if keyword:
            query = query.where(Archive.title.contains(keyword))
            count_query = count_query.where(Archive.title.contains(keyword))
        if tag:
            query = query.where(Archive.tags.contains(tag))
            count_query = count_query.where(Archive.tags.contains(tag))

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Archive.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def get_by_id(self, archive_id: str, user: User) -> Archive | None:
        result = await self.db.execute(select(Archive).where(Archive.id == archive_id))
        archive = result.scalar_one_or_none()
        if not archive:
            return None
        # 权限检查
        allowed = ACCESS_LEVELS.get(user.role, ["public"])
        if archive.access_level not in allowed:
            return None
        return archive

    async def create(self, user: User, data: ArchiveCreate) -> Archive:
        archive = Archive(
            community_id=user.community_id,
            title=data.title,
            description=data.description,
            file_url=data.fileUrl,
            file_name=data.fileName,
            file_hash=data.fileHash,
            category=data.category,
            access_level=data.accessLevel,
            uploaded_by=user.id,
        )
        archive.set_tags(data.tags)
        self.db.add(archive)
        await self.db.flush()
        logger.info(f"档案创建: {archive.id}")
        return archive

    async def delete(self, archive_id: str) -> bool:
        result = await self.db.execute(select(Archive).where(Archive.id == archive_id))
        archive = result.scalar_one_or_none()
        if not archive:
            return False
        await self.db.delete(archive)
        await self.db.flush()
        return True
