"""财务路由 — CRUD + 审批"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import FinanceReport, FinanceItem, User
from app.middleware.auth import get_current_user, require_role
from app.schemas.finance import (
    FinanceListOut, FinanceDetailOut, FinanceItemOut,
    FinanceCreate,
)

router = APIRouter()


def report_to_list_out(report: FinanceReport) -> FinanceListOut:
    """ORM → 列表输出"""
    return FinanceListOut(
        reportId=report.id,
        month=report.month,
        title=report.title,
        status=report.status,
        submittedBy=report.submitted_by,
        submittedAt=report.submitted_at,
        approvedBy=report.approved_by,
        approvedAt=report.approved_at,
        totalIncome=float(report.total_income or 0),
        totalExpense=float(report.total_expense or 0),
        balance=float(report.balance or 0),
    )


@router.get("", response_model=dict)
async def get_finance_list(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取财务报表列表"""
    query = select(FinanceReport)
    if current_user.community_id:
        query = query.where(FinanceReport.community_id == current_user.community_id)
    query = query.order_by(FinanceReport.created_at.desc())

    result = await db.execute(query)
    reports = result.scalars().all()

    report_outs = [report_to_list_out(r) for r in reports]
    return {"data": report_outs, "total": len(report_outs)}


@router.get("/{report_id}", response_model=FinanceDetailOut)
async def get_finance_detail(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取财务报表详情"""
    result = await db.execute(select(FinanceReport).where(FinanceReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")

    base = report_to_list_out(report)
    items = [
        FinanceItemOut(
            itemType=item.item_type,
            category=item.category,
            amount=float(item.amount or 0),
            description=item.description,
        )
        for item in report.items
    ]

    return FinanceDetailOut(**base.model_dump(), items=items)


@router.post("")
async def create_finance_report(
    req: FinanceCreate,
    current_user: User = Depends(require_role("property")),
    db: AsyncSession = Depends(get_db),
):
    """上报财务报表（仅物业）"""
    now = datetime.now()

    # 计算汇总
    total_income = sum(i.amount for i in req.items if i.itemType == "income")
    total_expense = sum(i.amount for i in req.items if i.itemType == "expense")
    balance = total_income - total_expense

    report = FinanceReport(
        community_id=current_user.community_id,
        month=req.month,
        title=req.title,
        status="pending",
        submitted_by=current_user.id,
        submitted_at=now,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
    )
    db.add(report)
    await db.flush()

    # 创建明细
    for item in req.items:
        fi = FinanceItem(
            report_id=report.id,
            item_type=item.itemType,
            category=item.category,
            amount=item.amount,
            description=item.description,
        )
        db.add(fi)

    await db.flush()
    return {"success": True, "reportId": report.id}


@router.post("/{report_id}/approve")
async def approve_finance_report(
    report_id: str,
    current_user: User = Depends(require_role("committee")),
    db: AsyncSession = Depends(get_db),
):
    """审批财务报表（仅业委会）"""
    result = await db.execute(select(FinanceReport).where(FinanceReport.id == report_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")
    if report.status != "pending":
        raise HTTPException(status_code=400, detail="报表已审批")

    report.status = "published"
    report.approved_by = current_user.id
    report.approved_at = datetime.now()

    # 重新计算汇总（确保一致性）
    total_income = sum(float(i.amount or 0) for i in report.items if i.item_type == "income")
    total_expense = sum(float(i.amount or 0) for i in report.items if i.item_type == "expense")
    report.total_income = total_income
    report.total_expense = total_expense
    report.balance = total_income - total_expense

    db.add(report)
    await db.flush()

    return {"success": True}
