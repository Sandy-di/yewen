"""用户路由 — 个人信息/房产/核验"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User, UserProperty
from app.middleware.auth import get_current_user
from app.schemas.user import UserUpdate, PropertyOut, VerifyRequest, VerifyResponse

router = APIRouter()


@router.put("/profile")
async def update_profile(
    req: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新用户信息"""
    if req.nickname is not None:
        current_user.nickname = req.nickname
    if req.phone is not None:
        current_user.phone = req.phone
    if req.avatar is not None:
        current_user.avatar = req.avatar

    db.add(current_user)
    await db.flush()
    return {"success": True}


@router.get("/properties", response_model=list[PropertyOut])
async def get_properties(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户房产列表"""
    result = await db.execute(
        select(UserProperty).where(UserProperty.user_id == current_user.id)
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


@router.post("/verify", response_model=VerifyResponse)
async def verify_identity(
    req: VerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    身份核验
    L1: 手机验证码（模拟）
    L2: 手机号+房产信息匹配
    L3: 姓名+身份证+房产证
    L4: 微信人脸核身
    """
    if req.level < 1 or req.level > 4:
        return VerifyResponse(success=False, verifiedLevel=current_user.verified_level)

    # 模拟核验：直接通过
    if req.level > current_user.verified_level:
        current_user.verified_level = req.level
        db.add(current_user)
        await db.flush()

    return VerifyResponse(success=True, verifiedLevel=current_user.verified_level)
