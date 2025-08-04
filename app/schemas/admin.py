from pydantic import BaseModel, EmailStr
from typing import Optional


class AdminLoginRequest(BaseModel):
    """Schema for admin login request"""
    email: EmailStr
    password: str


class AdminLoginResponse(BaseModel):
    """Schema for admin login response"""
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    message: str = "Admin login successful"


class AdminInfo(BaseModel):
    """Schema for admin user information"""
    id: int
    email: str
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True 