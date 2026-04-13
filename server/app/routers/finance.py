"""财务路由 — CRUD + 审批/拒绝"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.models import User
from app.middleware.auth import get_current_user, require_role
from app.schemas.finance import (
    FinanceListOut, FinanceDetailOut, FinanceItemOut, FinanceAttachmentOut,
    FinanceQuestionOut, FinanceCreate, FinanceRejectRequest,
    FinanceQuestionCreate, FinanceQuestionAnswer,
)
from app.services.finance_service import FinanceService

router = APIRouter()


def report_to_list_out(report) -> FinanceListOut:
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
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取财务报表列表"""
    service = FinanceService(db)
    reports, total = await service.get_list(
        current_user.community_id,
        status=status,
        page=page,
        page_size=pageSize,
    )
    report_outs = [report_to_list_out(r).model_dump() for r in reports]
    return {"data": report_outs, "total": total, "page": page, "pageSize": pageSize}


@router.get("/{report_id}", response_model=FinanceDetailOut)
async def get_finance_detail(
    report_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取财务报表详情"""
    service = FinanceService(db)
    report = await service.get_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")

    base = report_to_list_out(report)
    items = [
        FinanceItemOut(
            itemType=item.item_type,
            category=item.category,
            amount=float(item.amount or 0),
            description=item.description,
            receiptUrl=item.receipt_url or "",
        )
        for item in report.items
    ]

    attachments = [
        FinanceAttachmentOut(
            name=a.get("name", ""),
            url=a.get("url", ""),
            size=a.get("size", 0),
        )
        for a in report.get_attachments()
    ]

    # 业主提问
    from app.models import FinanceQuestion
    questions_result = await db.execute(
        select(FinanceQuestion).where(FinanceQuestion.report_id == report_id).order_by(FinanceQuestion.created_at.desc())
    )
    questions = [
        FinanceQuestionOut(
            id=q.id,
            itemId=q.item_id,
            userId=q.user_id,
            question=q.question,
            answer=q.answer,
            answeredBy=q.answered_by,
            answeredAt=q.answered_at,
            createdAt=q.created_at,
        )
        for q in questions_result.scalars().all()
    ]

    return FinanceDetailOut(**base.model_dump(), items=items, attachments=attachments, questions=questions)


@router.post("")
async def create_finance_report(
    req: FinanceCreate,
    current_user: User = Depends(require_role("property")),
    db: AsyncSession = Depends(get_db),
):
    """上报财务报表（仅物业）"""
    service = FinanceService(db)
    report = await service.create(current_user, req)
    return {"success": True, "reportId": report.id}


@router.post("/{report_id}/approve")
async def approve_finance_report(
    report_id: str,
    current_user: User = Depends(require_role("committee")),
    db: AsyncSession = Depends(get_db),
):
    """审批财务报表（仅业委会）"""
    service = FinanceService(db)
    try:
        await service.approve(report_id, current_user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}


@router.post("/{report_id}/reject")
async def reject_finance_report(
    report_id: str,
    req: FinanceRejectRequest,
    current_user: User = Depends(require_role("committee")),
    db: AsyncSession = Depends(get_db),
):
    """拒绝/退回财务报表（仅业委会）"""
    service = FinanceService(db)
    try:
        await service.reject(report_id, current_user, req.reason)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}


@router.post("/{report_id}/questions")
async def create_finance_question(
    report_id: str,
    req: FinanceQuestionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """业主对财务报表提问"""
    from app.models import FinanceQuestion
    question = FinanceQuestion(
        report_id=report_id,
        item_id=req.itemId,
        user_id=current_user.id,
        question=req.question,
    )
    db.add(question)
    await db.flush()
    return {"success": True, "id": question.id}


@router.post("/{report_id}/questions/{question_id}/answer")
async def answer_finance_question(
    report_id: str,
    question_id: str,
    req: FinanceQuestionAnswer,
    current_user: User = Depends(require_role("property", "committee")),
    db: AsyncSession = Depends(get_db),
):
    """物业/业委会回答业主提问"""
    from app.models import FinanceQuestion
    from datetime import datetime, timezone

    result = await db.execute(
        select(FinanceQuestion).where(FinanceQuestion.id == question_id)
    )
    question = result.scalar_one_or_none()
    if not question:
        raise HTTPException(status_code=404, detail="提问不存在")
    question.answer = req.answer
    question.answered_by = current_user.id
    question.answered_at = datetime.now(timezone.utc)
    db.add(question)
    await db.flush()
    return {"success": True}
