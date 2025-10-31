from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SocialAccountBase(BaseModel):
    platform: str
    username: str


class SocialAccountCreate(SocialAccountBase):
    access_token: str


class SocialAccountRead(SocialAccountBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    connected: bool

    class Config:
        from_attributes = True
