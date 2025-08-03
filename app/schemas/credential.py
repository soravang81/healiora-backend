from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CredentialLogin(BaseModel):
    email: str
    password: str

class CredentialBase(BaseModel):
    email: str
    role: Optional[str] = None

class CredentialCreate(BaseModel):
    email: str
    password: str
    role: str = "patient"

class CredentialOut(BaseModel):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserDataResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # Profile data based on role
    profile_data: Optional[dict] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
