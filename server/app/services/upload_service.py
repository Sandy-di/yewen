"""文件上传服务 — 本地存储 + 预留对象存储接口"""

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from fastapi import UploadFile

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger("upload_service")

# 允许的文件类型
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".pdf", ".doc", ".docx"}


class UploadService:
    def __init__(self):
        self.settings = get_settings()
        self.upload_dir = Path(self.settings.UPLOAD_DIR)
        self.max_size = self.settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    async def upload(self, file: UploadFile) -> dict:
        """
        上传文件，返回 {url, filename}
        """
        # 校验文件名
        if not file.filename:
            raise ValueError("文件名不能为空")

        # 校验扩展名
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise ValueError(f"不支持的文件类型: {ext}，允许: {', '.join(ALLOWED_EXTENSIONS)}")

        # 读取文件内容并校验大小
        content = await file.read()
        if len(content) > self.max_size:
            raise ValueError(f"文件大小超过限制（{self.settings.MAX_UPLOAD_SIZE_MB}MB）")

        # 生成唯一文件名
        date_prefix = datetime.now(timezone.utc).strftime("%Y%m%d")
        unique_name = f"{date_prefix}_{uuid.uuid4().hex[:8]}{ext}"

        # 确保目录存在
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        # 保存文件
        file_path = self.upload_dir / unique_name
        with open(file_path, "wb") as f:
            f.write(content)

        # 生成访问URL
        url = f"/uploads/{unique_name}"
        logger.info(f"文件上传: {unique_name} ({len(content)} bytes)")

        return {"url": url, "filename": unique_name}
