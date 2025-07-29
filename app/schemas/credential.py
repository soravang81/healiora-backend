from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class CredentialBase(BaseModel):
    email: EmailStr
    phone_number: Optional[str] = None

class CredentialCreate(CredentialBase):
    password: str
    role: str = "patient"  # Default role is patient

class CredentialLogin(BaseModel):
    email: EmailStr
    password: str

class CredentialUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None

class CredentialOut(CredentialBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
