"""档案路由 — CRUD + 权限过滤"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.models import User
from app.middleware.auth import get_current_user, require_role
from app.schemas.archive import ArchiveListOut, ArchiveDetailOut, ArchiveCreate
from app.services.archive_service import ArchiveService

router = APIRouter()


def archive_to_out(a) -> ArchiveListOut:
    return ArchiveListOut(
        id=a.id, title=a.title, category=a.category, accessLevel=a.access_level,
        fileName=a.file_name, tags=a.get_tags(), uploadedBy=a.uploaded_by, createdAt=a.created_at,
    )


@router.get("", response_model=dict)
async def get_archive_list(
    category: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ArchiveService(db)
    archives, total = await service.get_list(
        current_user, category=category, keyword=keyword, tag=tag, page=page, page_size=pageSize,
    )
    outs = [archive_to_out(a).model_dump() for a in archives]
    return {"data": outs, "total": total, "page": page, "pageSize": pageSize}


@router.get("/{archive_id}", response_model=ArchiveDetailOut)
async def get_archive_detail(
    archive_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ArchiveService(db)
    archive = await service.get_by_id(archive_id, current_user)
    if not archive:
        raise HTTPException(status_code=404, detail="档案不存在或无权查看")
    base = archive_to_out(archive)
    return ArchiveDetailOut(**base.model_dump(), description=archive.description, fileUrl=archive.file_url, fileHash=archive.file_hash)


@router.post("")
async def create_archive(
    req: ArchiveCreate,
    current_user: User = Depends(require_role("committee")),
    db: AsyncSession = Depends(get_db),
):
    service = ArchiveService(db)
    archive = await service.create(current_user, req)
    return {"success": True, "id": archive.id}


@router.delete("/{archive_id}")
async def delete_archive(
    archive_id: str,
    current_user: User = Depends(require_role("committee")),
    db: AsyncSession = Depends(get_db),
):
    service = ArchiveService(db)
    deleted = await service.delete(archive_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="档案不存在")
    return {"success": True}
