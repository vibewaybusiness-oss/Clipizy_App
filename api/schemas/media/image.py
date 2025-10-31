from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ImageBase(BaseModel):
    prompt: Optional[str] = None


class ImageCreate(ImageBase):
    pass


class ImageRead(ImageBase):
    id: UUID
    project_id: UUID
    user_id: UUID
    file_path: str
    width: Optional[int]
    height: Optional[int]
    format: Optional[str]
    size_mb: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True
