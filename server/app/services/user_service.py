"""用户服务 — 个人信息/房产/核验 + 管理端用户管理"""

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserProperty, RoleChangeLog
from app.schemas.user import UserUpdate, PropertyOut
from app.utils.logger import get_logger

logger = get_logger("user_service")

# 中文 → 英文角色映射
ROLE_CN_TO_EN = {
    "业主": "owner",
    "物业": "property",
    "业委会": "committee",
    "owner": "owner",
    "property": "property",
    "committee": "committee",
}

# 英文 → 中文角色映射
ROLE_EN_TO_CN = {
    "owner": "业主",
    "property": "物业",
    "committee": "业委会",
}


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_profile(self, user: User, data: UserUpdate) -> None:
        """更新用户信息"""
        if data.nickname is not None:
            user.nickname = data.nickname
        if data.phone is not None:
            user.phone = data.phone
        if data.avatar is not None:
            user.avatar = data.avatar
        self.db.add(user)
        await self.db.flush()

    async def get_properties(self, user_id: str) -> list[PropertyOut]:
        """获取用户房产列表"""
        result = await self.db.execute(
            select(UserProperty).where(UserProperty.user_id == user_id)
        )
        properties = result.scalars().all()
        return [
            PropertyOut(
                propertyId=p.id,
                building=p.building,
                unit=p.unit,
                roomNo=p.room_no,
                usableArea=p.usable_area,
                isDefault=p.is_default,
            )
            for p in properties
        ]

    async def verify_identity(self, user: User, level: int) -> int:
        """身份核验（模拟），返回核验后的等级"""
        if level < 1 or level > 4:
            return user.verified_level
        if level > user.verified_level:
            user.verified_level = level
            self.db.add(user)
            await self.db.flush()
            logger.info(f"用户 {user.id} 核验等级提升至 L{level}")
        return user.verified_level

    async def update_role(self, user_id: str, role: str, operated_by: str | None = None, reason: str = "") -> None:
        """修改用户角色 — 支持中文输入，记录变更日志"""
        # 中文 → 英文映射
        role_en = ROLE_CN_TO_EN.get(role)
        if not role_en:
            raise ValueError(f"无效的角色：{role}，请输入 业主/物业/业委会")

        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("用户不存在")

        old_role = user.role
        if old_role == role_en:
            return  # 角色未变，无需操作

        # 更新角色
        user.role = role_en
        self.db.add(user)

        # 写入变更记录（公示用，不可删除）
        log = RoleChangeLog(
            user_id=user_id,
            old_role=old_role,
            new_role=role_en,
            reason=reason,
            operated_by=operated_by,
        )
        self.db.add(log)
        await self.db.flush()
        logger.info(f"用户 {user_id} 角色从 {old_role} 变更为 {role_en}，操作者: {operated_by}，原因: {reason}")

    async def get_role_logs(self, community_id: str | None = None, page: int = 1, page_size: int = 20) -> tuple[list[RoleChangeLog], int]:
        """获取角色变更记录（公示，不可删除）"""
        query = select(RoleChangeLog).order_by(RoleChangeLog.created_at.desc())
        count_query = select(func.count(RoleChangeLog.id))

        if community_id:
            # 通过用户表关联筛选同社区
            query = query.join(User, RoleChangeLog.user_id == User.id).where(User.community_id == community_id)
            count_query = count_query.join(User, RoleChangeLog.user_id == User.id).where(User.community_id == community_id)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        logs = result.scalars().all()
        return logs, total

    async def toggle_active(self, user_id: str, is_active: bool) -> None:
        """启用/禁用用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("用户不存在")
        user.is_active = is_active
        self.db.add(user)
        await self.db.flush()
        logger.info(f"用户 {user_id} 状态修改为 {'启用' if is_active else '禁用'}")

    async def bind_community(self, user: User, community_id: str) -> None:
        """绑定用户到社区"""
        user.community_id = community_id
        self.db.add(user)
        await self.db.flush()
        logger.info(f"用户 {user.id} 绑定社区 {community_id}")
