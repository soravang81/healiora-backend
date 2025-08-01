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

class AmbulanceUpdate(BaseModel):
    ambulance_number: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    driver_email: Optional[EmailStr] = None
    vehicle_type: Optional[str] = None

class AmbulanceLogin(BaseModel):
    email: EmailStr
    password: str

class AmbulanceOut(AmbulanceBase):
    id: int
    credential_id: int
    hospital_id: int

    class Config:
        orm_mode = True 