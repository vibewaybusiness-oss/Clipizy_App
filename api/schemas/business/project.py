from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from api.models.project import ProjectStatus


class ProjectBase(BaseModel):
    type: str
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None


class ProjectRead(ProjectBase):
    id: UUID
    user_id: UUID
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
