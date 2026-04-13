"""社区管理路由 — CRUD + 搜索"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Community, User
from app.middleware.auth import get_current_user, require_role
from app.schemas.community import CommunityOut, CommunityCreate, CommunityUpdate
from app.services.community_service import CommunityService

router = APIRouter()


@router.get("/search", response_model=dict)
async def search_communities(
    keyword: str = Query("", max_length=50, description="搜索关键词"),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """搜索社区（免登录，用于用户选择社区）"""
    query = select(Community)
    count_query = select(func.count(Community.id))

    if keyword:
        pattern = f"%{keyword}%"
        query = query.where(or_(Community.name.ilike(pattern), Community.address.ilike(pattern)))
        count_query = count_query.where(or_(Community.name.ilike(pattern), Community.address.ilike(pattern)))

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Community.name).offset((page - 1) * pageSize).limit(pageSize)
    result = await db.execute(query)
    communities = result.scalars().all()

    return {
        "data": [CommunityOut.model_validate(c).model_dump() for c in communities],
        "total": total,
        "page": page,
        "pageSize": pageSize,
    }


@router.get("", response_model=dict)
async def get_communities(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取社区列表"""
    service = CommunityService(db)
    items, total = await service.get_list(page=page, page_size=pageSize)
    return {
        "data": [CommunityOut.model_validate(c).model_dump() for c in items],
        "total": total,
        "page": page,
        "pageSize": pageSize,
    }


@router.get("/{community_id}", response_model=CommunityOut)
async def get_community(
    community_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取社区详情"""
    service = CommunityService(db)
    community = await service.get_by_id(community_id)
    if not community:
        raise HTTPException(status_code=404, detail="社区不存在")
    return CommunityOut.model_validate(community)


@router.post("")
async def create_community(
    req: CommunityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("committee")),
):
    """创建社区（仅业委会）"""
    service = CommunityService(db)
    try:
        community = await service.create(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True, "id": community.id}


@router.put("/{community_id}")
async def update_community(
    community_id: str,
    req: CommunityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("committee")),
):
    """更新社区信息（仅业委会）"""
    service = CommunityService(db)
    try:
        community = await service.update(community_id, req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not community:
        raise HTTPException(status_code=404, detail="社区不存在")
    return {"success": True}
