from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class VideoBase(BaseModel):
    prompt: Optional[str] = None


class VideoCreate(VideoBase):
    pass


class VideoRead(VideoBase):
    id: UUID
    project_id: UUID
    user_id: UUID
    file_path: str
    duration: Optional[float]
    resolution: Optional[str]
    format: Optional[str]
    aspect_ratio: Optional[str]
    size_mb: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True
