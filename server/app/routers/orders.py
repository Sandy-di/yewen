"""报修工单路由 — CRUD + 状态机 + 评价/复修"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import RepairOrder, OrderTimeline, User, UserProperty
from app.middleware.auth import get_current_user, require_role
from app.schemas.order import (
    OrderListOut, OrderDetailOut, TimelineOut,
    OrderCreate, OrderCreateResponse, RateRequest, ReworkRequest,
)

router = APIRouter()

# 合法状态流转
VALID_TRANSITIONS = {
    "submitted": ["accepted"],
    "accepted": ["processing"],
    "processing": ["pending_check"],
    "pending_check": ["completed", "rework"],
    "rework": ["processing"],
    "completed": [],
}


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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取工单列表"""
    query = select(RepairOrder)

    # 业主只能看自己的工单，物业/业委会看所有
    if current_user.role == "owner":
        query = query.where(RepairOrder.user_id == current_user.id)
    elif current_user.community_id:
        query = query.where(RepairOrder.community_id == current_user.community_id)

    if status and status != "all":
        query = query.where(RepairOrder.status == status)
    query = query.order_by(RepairOrder.created_at.desc())

    result = await db.execute(query)
    orders = result.scalars().all()

    order_outs = [order_to_list_out(o) for o in orders]
    return {"data": order_outs, "total": len(order_outs)}


@router.get("/{order_id}", response_model=OrderDetailOut)
async def get_order_detail(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取工单详情"""
    result = await db.execute(select(RepairOrder).where(RepairOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")

    # 权限检查
    if current_user.role == "owner" and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权查看此工单")

    base = order_to_list_out(order)

    # 获取房产名称
    prop_name = ""
    if order.property_id:
        prop_result = await db.execute(select(UserProperty).where(UserProperty.id == order.property_id))
        prop = prop_result.scalar_one_or_none()
        if prop:
            prop_name = f"{prop.building}{prop.unit}{prop.room_no}"

    import json
    return OrderDetailOut(
        **base.model_dump(),
        propertyId=order.property_id,
        propertyName=prop_name,
        photos=json.loads(order.photos) if isinstance(order.photos, str) else order.photos,
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
    # 获取用户默认房产
    prop_result = await db.execute(
        select(UserProperty).where(
            UserProperty.user_id == current_user.id,
            UserProperty.is_default == True,
        )
    )
    default_prop = prop_result.scalar_one_or_none()

    import json
    now = datetime.now()
    order = RepairOrder(
        community_id=current_user.community_id,
        user_id=current_user.id,
        category=req.category,
        sub_category=req.subCategory,
        description=req.description,
        photos=json.dumps(req.photos),
        status="submitted",
        property_id=default_prop.id if default_prop else None,
        contact_phone=req.contactPhone or current_user.phone,
        sla_level=24,
        sla_deadline=now + timedelta(hours=24),
    )
    db.add(order)
    await db.flush()

    # 添加时间线
    timeline = OrderTimeline(
        order_id=order.id,
        content="业主提交报修",
        type="submitted",
    )
    db.add(timeline)
    await db.flush()

    return OrderCreateResponse(success=True, orderId=order.id)


@router.post("/{order_id}/accept")
async def accept_order(
    order_id: str,
    current_user: User = Depends(require_role("property")),
    db: AsyncSession = Depends(get_db),
):
    """接单（仅物业）"""
    result = await db.execute(select(RepairOrder).where(RepairOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")

    if order.status != "submitted":
        raise HTTPException(status_code=400, detail=f"工单状态为{order.status}，无法接单")

    order.status = "accepted"
    order.accepted_at = datetime.now()
    order.accepted_by = current_user.id
    db.add(order)

    timeline = OrderTimeline(
        order_id=order.id,
        content=f"物业已接单",
        type="accepted",
    )
    db.add(timeline)
    await db.flush()

    return {"success": True}


@router.post("/{order_id}/process")
async def process_order(
    order_id: str,
    current_user: User = Depends(require_role("property")),
    db: AsyncSession = Depends(get_db),
):
    """开始处理（仅物业）"""
    result = await db.execute(select(RepairOrder).where(RepairOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")

    if order.status != "accepted" and order.status != "rework":
        raise HTTPException(status_code=400, detail=f"工单状态为{order.status}，无法开始处理")

    order.status = "processing"
    db.add(order)

    timeline = OrderTimeline(
        order_id=order.id,
        content="开始维修处理",
        type="processing",
    )
    db.add(timeline)
    await db.flush()

    return {"success": True}


@router.post("/{order_id}/complete")
async def complete_order(
    order_id: str,
    note: str = "",
    current_user: User = Depends(require_role("property")),
    db: AsyncSession = Depends(get_db),
):
    """完成维修（仅物业）"""
    result = await db.execute(select(RepairOrder).where(RepairOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")

    if order.status != "processing":
        raise HTTPException(status_code=400, detail=f"工单状态为{order.status}，无法完成")

    order.status = "pending_check"
    order.completed_at = datetime.now()
    order.completion_note = note
    db.add(order)

    timeline = OrderTimeline(
        order_id=order.id,
        content=f"维修完成{('：' + note) if note else ''}",
        type="completed",
    )
    db.add(timeline)
    await db.flush()

    return {"success": True}


@router.post("/{order_id}/rate")
async def rate_order(
    order_id: str,
    req: RateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """评价工单"""
    result = await db.execute(select(RepairOrder).where(RepairOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能评价自己的工单")
    if order.status != "pending_check":
        raise HTTPException(status_code=400, detail="工单状态不允评价")

    order.rating = req.rating
    order.rating_comment = req.comment
    order.status = "completed"
    db.add(order)

    timeline = OrderTimeline(
        order_id=order.id,
        content=f"业主验收通过，评价{req.rating}星",
        type="verified",
    )
    db.add(timeline)
    await db.flush()

    return {"success": True}


@router.post("/{order_id}/rework")
async def rework_order(
    order_id: str,
    req: ReworkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """申请复修"""
    result = await db.execute(select(RepairOrder).where(RepairOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="工单不存在")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能对自己的工单申请复修")
    if order.status != "pending_check":
        raise HTTPException(status_code=400, detail="工单状态不允许复修")

    order.status = "rework"
    db.add(order)

    timeline = OrderTimeline(
        order_id=order.id,
        content=f"业主申请复修：{req.reason}",
        type="rework",
    )
    db.add(timeline)
    await db.flush()

    return {"success": True}
