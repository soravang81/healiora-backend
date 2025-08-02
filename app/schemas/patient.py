from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic.networks import EmailStr

class PatientBase(BaseModel):
    full_name: Optional[str] = None
    email: EmailStr
    password: str

class PatientCreate(PatientBase):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    emergency_contact: Optional[str] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None

class PatientLogin(BaseModel):
    email: EmailStr
    password: str

class PatientOut(BaseModel):
    id: int
    credential_id: int
    email: EmailStr
    full_name: Optional[str] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    age: Optional[int] = None
    emergency_contact: Optional[str] = None
    created_at: Optional[datetime] = None  # if in your model

    class Config:
        from_attributes = True


class PatientRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    phone_number: str
    role: str = "patient"

    # Patient-specific fields
    username: str
    age: int
    emergency_contact: str

