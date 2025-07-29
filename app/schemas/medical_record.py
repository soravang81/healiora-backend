from pydantic import BaseModel
from datetime import date
from typing import Optional


class MedicalRecordBase(BaseModel):
    date_of_birth: date
    blood_group: Optional[str] = None
    past_surgeries: Optional[str] = None
    long_term_medications: Optional[str] = None
    ongoing_illnesses: Optional[str] = None
    allergies: Optional[str] = None
    other_issues: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_number: Optional[str] = None


class MedicalRecordCreate(MedicalRecordBase):
    pass


class MedicalRecordUpdate(MedicalRecordBase):
    pass


class MedicalRecordOut(MedicalRecordBase):
    id: int
    patient_id: int 

    class Config:
        from_attributes = True
