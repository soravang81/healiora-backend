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

class DoctorLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class PasswordChangeVerify(BaseModel):
    verification_code: str
