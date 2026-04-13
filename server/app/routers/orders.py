"""报修工单路由 — CRUD + 状态机 + 评价/复修"""

import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.models import RepairOrder, UserProperty, User
from app.middleware.auth import get_current_user, require_role
from app.schemas.order import (
    OrderListOut, OrderDetailOut, TimelineOut,
    OrderCreate, OrderCreateResponse, RateRequest, ReworkRequest, CompleteRequest,
)
from app.services.order_service import OrderService

router = APIRouter()


def order_to_list_out(order: RepairOrder) -> OrderListOut:
    """ORM → 列表输出"""
    timelines = [
        TimelineOut(
            time=t.created_at.strftime("%H:%M") if t.created_at else "",
            content=t.content,
            type=t.type,
        )
        for t in order.timelines
    ]
    return OrderListOut(
        orderId=order.id,
        category=order.category,
        subCategory=order.sub_category,
        description=order.description,
        status=order.status,
        contactPhone=order.contact_phone,
        createdAt=order.created_at,
        acceptedAt=order.accepted_at,
        acceptedBy=order.accepted_by,
        acceptorPhone=order.acceptor_phone,
        estimatedTime=order.estimated_time,
        slaDeadline=order.sla_deadline,
        timeline=timelines,
    )


@router.get("", response_model=dict)
async def get_order_list(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取工单列表"""
    service = OrderService(db)
    orders, total = await service.get_list(
        current_user,
        status=status,
        category=category,
        keyword=keyword,
        page=page,
        page_size=pageSize,
    )
    order_outs = [order_to_list_out(o).model_dump() for o in orders]
    return {"data": order_outs, "total": total, "page": page, "pageSize": pageSize}


@router.get("/{order_id}", response_model=OrderDetailOut)
async def get_order_detail(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取工单详情"""
    service = OrderService(db)
    order = await service.get_by_id(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 权限检查
    if current_user.role == "owner" and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此工单")

    base = order_to_list_out(order)

    # 获取房产名称
    prop_name = ""
    if order.property_id:
        prop_result = await db.execute(
            select(UserProperty).where(UserProperty.id == order.property_id)
        )
        prop = prop_result.scalar_one_or_none()
        if prop:
            prop_name = f"{prop.building}{prop.unit}{prop.room_no}"

    return OrderDetailOut(
        **base.model_dump(),
        propertyId=order.property_id,
        propertyName=prop_name,
        photos=json.loads(order.photos) if isinstance(order.photos, str) else order.photos,
        video=order.video or "",
        appointmentTime=order.appointment_time or "",
        completedAt=order.completed_at,
        completionPhotos=json.loads(order.completion_photos) if isinstance(order.completion_photos, str) else order.completion_photos,
        completionNote=order.completion_note,
        rating=order.rating,
        ratingComment=order.rating_comment,
        slaLevel=order.sla_level,
    )


@router.post("", response_model=OrderCreateResponse)
async def create_order(
    req: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交报修"""
    service = OrderService(db)
    order = await service.create(current_user, req)
    return OrderCreateResponse(success=True, orderId=order.id)


@router.post("/{order_id}/accept")
async def accept_order(
    order_id: str,
    current_user: User = Depends(require_role("property")),
    db: AsyncSession = Depends(get_db),
):
    """接单（仅物业）"""
    service = OrderService(db)
    try:
        await service.accept(order_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}


@router.post("/{order_id}/process")
async def process_order(
    order_id: str,
    current_user: User = Depends(require_role("property")),
    db: AsyncSession = Depends(get_db),
):
    """开始处理（仅物业）"""
    service = OrderService(db)
    try:
        await service.process(order_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}


@router.post("/{order_id}/complete")
async def complete_order(
    order_id: str,
    req: CompleteRequest,
    current_user: User = Depends(require_role("property")),
    db: AsyncSession = Depends(get_db),
):
    """完成维修（仅物业）"""
    service = OrderService(db)
    try:
        await service.complete(order_id, req.note, req.completionPhotos)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}


@router.post("/{order_id}/rate")
async def rate_order(
    order_id: str,
    req: RateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """评价工单"""
    service = OrderService(db)
    try:
        await service.rate(order_id, current_user, req.rating, req.comment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}


@router.post("/{order_id}/rework")
async def rework_order(
    order_id: str,
    req: ReworkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """申请复修"""
    service = OrderService(db)
    try:
        await service.rework(order_id, current_user, req.reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}
