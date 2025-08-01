from pydantic import BaseModel, EmailStr
from typing import Optional

class DoctorBase(BaseModel):
    name: str
    phone_number: str
    email: EmailStr
    address: Optional[str] = None
    education: Optional[str] = None
    specialization: Optional[str] = None
    years_of_experience: Optional[float] = None

class DoctorCreate(DoctorBase):
    pass

class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    education: Optional[str] = None
    specialization: Optional[str] = None
    years_of_experience: Optional[float] = None


class DoctorLogin(BaseModel):
    email: EmailStr
    password: str

class DoctorOut(DoctorBase):
    id: int
    credential_id: int
    hospital_id: int

    class Config:
        orm_mode = True
