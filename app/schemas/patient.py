from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic.networks import EmailStr

class PatientBase(BaseModel):
    username: str
    age: Optional[int] = None
    emergency_contact: Optional[str] = None

class PatientCreate(PatientBase):
    pass  # No extra fields; username, age, emergency contact

class PatientUpdate(BaseModel):
    username: Optional[str] = None
    age: Optional[int] = None
    emergency_contact: Optional[str] = None

class PatientOut(PatientBase):
    id: int
    credential_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CredentialCreate(BaseModel):
    email: EmailStr
    password: str
    phone_number: Optional[str] = None
    role: str  # e.g., "patient", "admin", "hospital"


class PatientRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    phone_number: str
    role: str = "patient"

    # Patient-specific fields
    username: str
    age: int
    emergency_contact: str
