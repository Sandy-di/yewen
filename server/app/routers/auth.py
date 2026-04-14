"""认证路由 — 微信登录 + 用户信息"""

from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.middleware.auth import get_current_user, create_token
from app.middleware.rate_limit import limiter
from app.schemas.auth import LoginRequest, LoginResponse, ProfileResponse, IdentitiesInfo
from app.services.auth_service import AuthService
from app.utils.wechat import code2session
from app.utils.logger import get_logger
from app.config import get_settings

router = APIRouter()
logger = get_logger("auth")


@router.post("/login", response_model=LoginResponse)
@limiter.limit("10/minute")
async def login(request: Request, req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    微信登录流程：
    1. 小程序 wx.login() 获取 code
    2. 后端用 code 换取 openid
    3. 查找/创建用户，返回 JWT token
    """
    settings = get_settings()
    openid = None
    unionid = None

    try:
        wx_data = await code2session(req.code)
        openid = wx_data["openid"]
        unionid = wx_data.get("unionid")
    except Exception:
        if not settings.WX_APPID:
            # 开发模式：使用 code 作为 openid
            openid = f"dev_{req.code}"
            unionid = None
        else:
            raise

    service = AuthService(db)
    return await service.login_with_openid(openid, unionid)


@router.post("/dev-token", response_model=LoginResponse, include_in_schema=True)
async def dev_token(openid: str, db: AsyncSession = Depends(get_db)):
    """
    【测试模式】直接用 openid 获取 token。
    在 DEBUG=True 或 TEST_MODE=True 时可用，方便测试种子数据用户。
    种子数据 openid:
      - oDev_Owner_001（业主）
      - oDev_Property_001（物业）
      - oDev_Committee_001（业委会）
    """
    settings = get_settings()
    if not settings.DEBUG and not settings.TEST_MODE:
        raise HTTPException(status_code=404, detail="Not Found")

    result = await db.execute(select(User).where(User.openid == openid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=f"用户不存在: {openid}")

    token = create_token(user.id, user.role)
    return LoginResponse(
        token=token,
        user_id=user.id,
        role=user.role,
        nickname=user.nickname,
        is_new=False,
    )


@router.post("/switch-role", response_model=LoginResponse, include_in_schema=True)
async def switch_role(
    openid: str,
    db: AsyncSession = Depends(get_db),
):
    """
    【测试模式】切换身份 — 通过 openid 切换到不同角色的用户。
    在 TEST_MODE=True 时可用。
    种子数据 openid:
      - oDev_Owner_001（业主：张先生）
      - oDev_Property_001（物业：物业服务中心）
      - oDev_Committee_001（业委会：张主任）
    """
    settings = get_settings()
    if not settings.TEST_MODE:
        raise HTTPException(status_code=404, detail="Not Found")

    result = await db.execute(select(User).where(User.openid == openid))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail=f"用户不存在: {openid}")

    token = create_token(user.id, user.role)
    return LoginResponse(
        token=token,
        user_id=user.id,
        role=user.role,
        nickname=user.nickname,
        is_new=False,
    )


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
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

    # 显式查询社区名称（避免 lazy loading 在 async 上下文中的问题）
    community_name = None
    if current_user.community_id:
        from app.models import Community
        comm_result = await db.execute(select(Community).where(Community.id == current_user.community_id))
        comm = comm_result.scalar_one_or_none()
        if comm:
            community_name = comm.name

    # 计算身份（叠加关系：业委会成员同时也是业主）
    identities = IdentitiesInfo(
        isOwner=current_user.role in ("owner", "committee"),
        isProperty=current_user.role == "property",
        isCommittee=current_user.role == "committee",
    )

    return ProfileResponse(
        userId=current_user.id,
        openid=current_user.openid,
        nickname=current_user.nickname,
        phone=current_user.phone,
        avatar=current_user.avatar,
        role=current_user.role,
        verifiedLevel=current_user.verified_level,
        communityId=current_user.community_id,
        communityName=community_name,
        identities=identities,
        properties=properties,
    )
