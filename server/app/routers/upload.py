"""文件上传路由"""

from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import limiter
from app.models import User
from app.services.upload_service import UploadService

router = APIRouter()


@router.post("")
@limiter.limit("20/minute")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """上传文件（图片/文档），返回访问URL"""
    service = UploadService()
    try:
        result = await service.upload(file)
        return {"success": True, "url": result["url"], "filename": result["filename"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
