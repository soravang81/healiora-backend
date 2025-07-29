from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# Shared base schema
class HospitalBase(BaseModel):
    name: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: str
    email: Optional[EmailStr] = None


# Schema for hospital creation (by admin)
class HospitalCreate(HospitalBase):
    user_id: int  # Must be an admin-assigned user


# Schema for hospital update
class HospitalUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    phone: Optional[str]
    email: Optional[EmailStr]
    pending: Optional[bool]
    approved: Optional[bool]


# Schema for DB response (what is returned to client)
class HospitalOut(HospitalBase):
    id: int
    user_id: int
    pending: bool
    approved: bool
    created_at: datetime

    class Config:
        orm_mode = True
