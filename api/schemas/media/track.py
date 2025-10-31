from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TrackBase(BaseModel):
    prompt: Optional[str] = None
    title: Optional[str] = None
    ai_generated: bool = False
    description: Optional[str] = None


class TrackCreate(TrackBase):
    pass


class TrackRead(TrackBase):
    id: UUID
    project_id: UUID
    file_path: str
    ai_generated: bool = False
    prompt: Optional[str] = None
    genre: Optional[str] = None
    instrumental: bool = False
    video_description: Optional[str] = None
    description: Optional[str] = None
    vibe: Optional[str] = None
    lyrics: Optional[str] = None
    version: int = 1
    status: str = "uploaded"
    track_metadata: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
