from pydantic import BaseModel, EmailStr
from typing import Optional

class DoctorBase(BaseModel):
    name: str
    phone_number: str
    email: EmailStr
    address: str
    education: str
    specialization: str
    years_of_experience: float

class DoctorCreate(DoctorBase):
    pass

class DoctorOut(DoctorBase):
    id: int
    hospital_id: int
    credential_id: int

    class Config:
        orm_mode = True

class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    education: Optional[str] = None
    specialization: Optional[str] = None
    years_of_experience: Optional[float] = None

class DoctorLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class PasswordChangeVerify(BaseModel):
    verification_code: str
