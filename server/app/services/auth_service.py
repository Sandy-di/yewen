"""认证服务 — 微信登录 + token管理"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Community
from app.middleware.auth import create_token
from app.schemas.auth import LoginResponse
from app.utils.logger import get_logger

logger = get_logger("auth_service")


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def login_with_openid(
        self, openid: str, unionid: str | None = None
    ) -> LoginResponse:
        """通过 openid 登录/注册，返回 JWT token"""
        result = await self.db.execute(select(User).where(User.openid == openid))
        user = result.scalar_one_or_none()
        is_new = False

        if not user:
            # 自动注册
            comm_result = await self.db.execute(select(Community).limit(1))
            community = comm_result.scalar_one_or_none()

            user = User(
                openid=openid,
                unionid=unionid,
                nickname="新用户",
                role="owner",
                verified_level=0,
                community_id=community.id if community else None,
            )
            self.db.add(user)
            await self.db.flush()
            is_new = True
            logger.info(f"新用户注册: openid={openid[:10]}...")

        token = create_token(user.id, user.role)

        return LoginResponse(
            token=token,
            user_id=user.id,
            role=user.role,
            nickname=user.nickname,
            is_new=is_new,
        )
