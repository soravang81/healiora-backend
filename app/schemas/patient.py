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

# New schema for initial registration (step 1)
class PatientInitialRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str

# Updated schema for additional details (step 2)
class PatientUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    emergency_contact: Optional[str] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None

# New schema for complete registration with auto-login
class PatientCompleteRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    age: int
    phone_number: str
    emergency_contact: str
    gender: str

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

# Response model for complete registration with token
class PatientRegisterResponse(BaseModel):
    patient: PatientOut
    access_token: str
    token_type: str = "bearer"

class PatientRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    phone_number: str
    role: str = "patient"

    # Patient-specific fields
    full_name: str
    gender: str
    age: int
    emergency_contact: str

