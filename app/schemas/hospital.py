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
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class HospitalOut(BaseModel):
    id: int
    name: str
    address: str
    phone: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime

    class Config:
        orm_mode = True
