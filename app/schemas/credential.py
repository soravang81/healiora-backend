from pydantic import BaseModel
from typing import Optional, Union
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

# Universal User Response Schema
class UniversalUserResponse(BaseModel):
    # Credential information
    id: int
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Patient-specific fields
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    emergency_contact: Optional[str] = None
    
    # Doctor-specific fields
    name: Optional[str] = None
    address: Optional[str] = None
    education: Optional[str] = None
    specialization: Optional[str] = None
    years_of_experience: Optional[int] = None
    
    # Ambulance-specific fields
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    ambulance_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    
    # Profile completion percentage
    profile_completion_percentage: Optional[int] = None

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
