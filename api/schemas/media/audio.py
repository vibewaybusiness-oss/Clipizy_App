from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class AudioBase(BaseModel):
    prompt: Optional[str] = None
    type: Optional[str] = "voiceover"  # voiceover, narration, sfx


class AudioCreate(AudioBase):
    pass


class AudioRead(AudioBase):
    id: UUID
    project_id: UUID
    user_id: UUID
    file_path: str
    duration: Optional[float]
    format: Optional[str]
    sample_rate: Optional[int]
    channels: Optional[int]
    size_mb: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True
