from typing import Optional

from pydantic import BaseModel, EmailStr


class OAuthTokenRequest(BaseModel):
    code: str
    state: Optional[str] = None


class OAuthUserInfo(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None
    provider: str  # 'google' or 'github'


class OAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 604800  # 7 days
    user: dict
