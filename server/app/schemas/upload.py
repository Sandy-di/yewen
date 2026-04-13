"""文件上传 Schema"""

from pydantic import BaseModel


class UploadResponse(BaseModel):
    """上传响应"""
    success: bool = True
    url: str
    filename: str
