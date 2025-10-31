from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class StatsRead(BaseModel):
    id: UUID
    project_id: UUID
    export_id: UUID
    user_id: UUID
    platform: str
    external_id: str
    views: int
    likes: int
    comments: int
    shares: int
    fetched_at: datetime

    class Config:
        from_attributes = True
