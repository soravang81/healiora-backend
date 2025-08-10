from pydantic import BaseModel, EmailStr
from typing import Optional

class AmbulanceBase(BaseModel):
    ambulance_number: str
    driver_name: str
    driver_phone: str
    driver_email: EmailStr
    vehicle_type: str

class AmbulanceCreate(AmbulanceBase):
    pass

class AmbulanceOut(AmbulanceBase):
    id: int
    hospital_id: int
    credential_id: int

    class Config:
        orm_mode = True

class AmbulanceLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class PasswordChangeVerify(BaseModel):
    verification_code: str 