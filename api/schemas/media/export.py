from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ExportBase(BaseModel):
    style: Optional[str] = None


class ExportCreate(ExportBase):
    pass


class ExportRead(ExportBase):
    id: UUID
    project_id: UUID
    user_id: UUID
    file_path: str
    duration: Optional[float]
    resolution: Optional[str]
    format: Optional[str]
    size_mb: Optional[float]
    credits_spent: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
