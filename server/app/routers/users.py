"""用户路由 — 个人信息/房产/核验 + 管理端用户管理"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel, Field

from app.database import get_db
from app.models import User, Community, RoleChangeLog
from app.middleware.auth import get_current_user, require_role
from app.schemas.user import (
    UserUpdate, UserListOut, PropertyOut,
    VerifyRequest, VerifyResponse, UserRoleUpdate, UserActiveUpdate,
)
from app.schemas.role_log import RoleLogOut
from app.services.user_service import UserService, ROLE_EN_TO_CN

router = APIRouter()


class BindCommunityRequest(BaseModel):
    """绑定社区请求"""
    communityId: str = Field(..., min_length=1, description="社区ID")


# ==================== 个人信息 ====================

@router.put("/profile")
async def update_profile(
    req: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新用户信息"""
    service = UserService(db)
    await service.update_profile(current_user, req)
    return {"success": True}


@router.get("/properties", response_model=list[PropertyOut])
async def get_properties(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户房产列表"""
    service = UserService(db)
    return await service.get_properties(current_user.id)


@router.post("/verify", response_model=VerifyResponse)
async def verify_identity(
    req: VerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """身份核验"""
    service = UserService(db)
    verified_level = await service.verify_identity(current_user, req.level)
    return VerifyResponse(success=True, verifiedLevel=verified_level)


# ==================== 管理端：用户管理 ====================

@router.get("/list", response_model=dict)
async def get_user_list(
    role: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_role("property", "committee")),
    db: AsyncSession = Depends(get_db),
):
    """获取用户列表（管理端）"""
    query = select(User)
    count_query = select(User)

    # 按社区过滤
    if current_user.community_id:
        query = query.where(User.community_id == current_user.community_id)
        count_query = count_query.where(User.community_id == current_user.community_id)

    if role and role != "all":
        query = query.where(User.role == role)
        count_query = count_query.where(User.role == role)
    if keyword:
        pattern = f"%{keyword}%"
        query = query.where((User.nickname.ilike(pattern)) | (User.phone.ilike(pattern)))
        count_query = count_query.where((User.nickname.ilike(pattern)) | (User.phone.ilike(pattern)))

    # 总数
    total_result = await db.execute(
        select(func.count()).select_from(count_query.subquery())
    )
    total = total_result.scalar() or 0

    # 分页
    query = query.order_by(User.created_at.desc())
    query = query.offset((page - 1) * pageSize).limit(pageSize)

    result = await db.execute(query)
    users = result.scalars().all()

    user_outs = [
        UserListOut(
            id=u.id,
            nickname=u.nickname,
            phone=u.phone,
            avatar=u.avatar,
            role=u.role,
            verifiedLevel=u.verified_level,
            communityId=u.community_id,
            isActive=u.is_active,
            createdAt=u.created_at,
        ).model_dump()
        for u in users
    ]
    return {"data": user_outs, "total": total, "page": page, "pageSize": pageSize}


@router.put("/community/bind")
async def bind_community(
    req: BindCommunityRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """绑定用户到社区"""
    # 验证社区存在
    result = await db.execute(select(Community).where(Community.id == req.communityId))
    community = result.scalar_one_or_none()
    if not community:
        raise HTTPException(status_code=404, detail="社区不存在")
    
    service = UserService(db)
    await service.bind_community(current_user, req.communityId)
    return {"success": True, "communityName": community.name}


@router.put("/{user_id}/role")
async def update_user_role(
    user_id: str,
    req: UserRoleUpdate,
    current_user: User = Depends(require_role("committee")),
    db: AsyncSession = Depends(get_db),
):
    """修改用户角色（仅业委会）— 支持中文输入"""
    service = UserService(db)
    try:
        await service.update_role(user_id, req.role, operated_by=current_user.id, reason=req.reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}


@router.put("/{user_id}/active")
async def toggle_user_active(
    user_id: str,
    req: UserActiveUpdate,
    current_user: User = Depends(require_role("committee")),
    db: AsyncSession = Depends(get_db),
):
    """启用/禁用用户（仅业委会）"""
    service = UserService(db)
    try:
        await service.toggle_active(user_id, req.isActive)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}


# ==================== 角色变更记录（公示，不可删除） ====================

@router.get("/role-logs", response_model=dict)
async def get_role_logs(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取角色变更记录（公示，不可删除）"""
    service = UserService(db)
    logs, total = await service.get_role_logs(
        community_id=current_user.community_id,
        page=page,
        page_size=pageSize,
    )

    # 批量查操作者昵称
    operator_ids = list({log.operated_by for log in logs if log.operated_by})
    operator_map = {}
    if operator_ids:
        result = await db.execute(select(User).where(User.id.in_(operator_ids)))
        for u in result.scalars().all():
            operator_map[u.id] = u.nickname or u.id

    log_outs = [
        RoleLogOut(
            id=log.id,
            userId=log.user_id,
            oldRole=log.old_role,
            newRole=log.new_role,
            oldRoleLabel=ROLE_EN_TO_CN.get(log.old_role, log.old_role),
            newRoleLabel=ROLE_EN_TO_CN.get(log.new_role, log.new_role),
            reason=log.reason,
            operatedBy=log.operated_by,
            operatorNickname=operator_map.get(log.operated_by, "") if log.operated_by else "",
            createdAt=log.created_at,
        ).model_dump()
        for log in logs
    ]
    return {"data": log_outs, "total": total, "page": page, "pageSize": pageSize}
