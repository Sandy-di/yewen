"""档案 Schema"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class ArchiveListOut(BaseModel):
    id: str
    title: str
    category: str
    accessLevel: str
    fileName: str = ""
    tags: List[str] = []
    uploadedBy: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArchiveDetailOut(ArchiveListOut):
    description: str = ""
    fileUrl: str = ""
    fileHash: str = ""


class ArchiveCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field("", max_length=2000)
    fileUrl: str = Field("", max_length=500)
    fileName: str = Field("", max_length=200)
    fileHash: str = Field("", max_length=64)
    category: str = Field("other", max_length=50)
    accessLevel: str = Field("public", pattern="^(public|internal|confidential)$")
    tags: List[str] = Field([])
