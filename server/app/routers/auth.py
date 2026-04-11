"""认证路由 — 微信登录 + 用户信息"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, Community
from app.middleware.auth import create_token, get_current_user
from app.schemas.auth import LoginRequest, LoginResponse, ProfileResponse
from app.utils.wechat import code2session

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    微信登录流程：
    1. 小程序 wx.login() 获取 code
    2. 后端用 code 换取 openid
    3. 查找/创建用户，返回 JWT token
    """
    try:
        wx_data = await code2session(req.code)
        openid = wx_data["openid"]
        unionid = wx_data.get("unionid")
    except Exception:
        # 开发模式：如果没有配置微信 appid/secret，使用 code 作为 openid
        from app.config import get_settings
        settings = get_settings()
        if not settings.WX_APPID:
            openid = f"dev_{req.code}"
            unionid = None
        else:
            raise

    # 查找用户
    result = await db.execute(select(User).where(User.openid == openid))
    user = result.scalar_one_or_none()
    is_new = False

    if not user:
        # 自动注册：查找默认社区
        comm_result = await db.execute(select(Community).limit(1))
        community = comm_result.scalar_one_or_none()

        user = User(
            openid=openid,
            unionid=unionid,
            nickname="新用户",
            role="owner",
            verified_level=0,
            community_id=community.id if community else None,
        )
        db.add(user)
        await db.flush()
        is_new = True

    token = create_token(user.id, user.role)

    return LoginResponse(
        token=token,
        user_id=user.id,
        role=user.role,
        nickname=user.nickname,
        is_new=is_new,
    )


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    properties = []
    for p in current_user.properties:
        properties.append({
            "propertyId": p.id,
            "building": p.building,
            "unit": p.unit,
            "roomNo": p.room_no,
            "usableArea": p.usable_area,
            "isDefault": p.is_default,
        })

    return ProfileResponse(
        userId=current_user.id,
        openid=current_user.openid,
        nickname=current_user.nickname,
        phone=current_user.phone,
        avatar=current_user.avatar,
        role=current_user.role,
        verifiedLevel=current_user.verified_level,
        communityId=current_user.community_id,
        properties=properties,
    )
