# app/schemas/hospital.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class HospitalCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    address: str
    phone: str
    admin_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    hospital_type: Optional[str] = None  # "government" or "private"
    emergency_available: Optional[bool] = None
    available_24_7: Optional[bool] = None
    registration_number: Optional[str] = None
    departments: Optional[str] = None  # Comma-separated list of departments

class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    hospital_type: Optional[str] = None
    emergency_available: Optional[bool] = None
    available_24_7: Optional[bool] = None
    registration_number: Optional[str] = None
    departments: Optional[str] = None

class HospitalOut(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    admin_name: Optional[str] = None
    created_at: datetime
    hospital_type: Optional[str] = None
    emergency_available: Optional[bool] = None
    available_24_7: Optional[bool] = None
    registration_number: Optional[str] = None
    departments: Optional[str] = None

    class Config:
        orm_mode = True
