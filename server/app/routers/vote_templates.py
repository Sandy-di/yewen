"""投票模板路由 — 查询预设模板"""

import json
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import User
from app.middleware.auth import get_current_user
from app.schemas.vote_template import VoteTemplateOut
from app.services.vote_template_service import VoteTemplateService

router = APIRouter()


@router.get("", response_model=dict)
async def get_vote_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取所有投票场景模板"""
    service = VoteTemplateService(db)
    templates = await service.get_all()
    outs = [
        VoteTemplateOut(
            id=t.id,
            name=t.name,
            description=t.description,
            voteType=t.vote_type,
            verificationLevel=t.verification_level,
            optionsTemplate=json.loads(t.options_template) if isinstance(t.options_template, str) else t.options_template,
            descriptionTemplate=t.description_template,
            sortOrder=t.sort_order,
        ).model_dump()
        for t in templates
    ]
    return {"data": outs}
