from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.medical_records import MedicalRecord
from app.db.models.patient import Patient
from app.db.models.credential import Credential
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate

def create_medical_record(db: Session, user_id: int, record_data: MedicalRecordCreate):
    """Create a medical record for a user"""
    return create_patient_medical_record(db, user_id, record_data)

def create_patient_medical_record(db: Session, credential_id: int, record_data: MedicalRecordCreate):
    # Ensure the user is a patient
    credential = db.query(Credential).filter(Credential.id == credential_id).first()
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    if credential.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can have medical records")

    # Find or create Patient instance linked to this credential
    patient = db.query(Patient).filter(Patient.credential_id == credential_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    # Prevent duplicate records
    existing = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Medical record already exists")

    # Create medical record
    record = MedicalRecord(patient_id=patient.id, **record_data.dict())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_medical_record(db: Session, user_id: int):
    """Get medical record for a user"""
    return get_patient_medical_record(db, user_id)

def get_patient_medical_record(db: Session, credential_id: int):
    patient = db.query(Patient).filter(Patient.credential_id == credential_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    record = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")
    return record

def update_medical_record(db: Session, user_id: int, update_data: MedicalRecordUpdate):
    """Update medical record for a user"""
    return update_patient_medical_record(db, user_id, update_data)

def update_patient_medical_record(db: Session, credential_id: int, update_data: MedicalRecordUpdate):
    patient = db.query(Patient).filter(Patient.credential_id == credential_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    record = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record

def delete_medical_record(db: Session, user_id: int):
    """Delete medical record for a user"""
    return delete_patient_medical_record(db, user_id)

def delete_patient_medical_record(db: Session, credential_id: int):
    patient = db.query(Patient).filter(Patient.credential_id == credential_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    record = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient.id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Medical record not found")

    db.delete(record)
    db.commit()
    return {"detail": "Medical record deleted successfully"}


def get_medical_record_by_patient_id(db: Session, patient_id: int):
    """
    Get medical record by patient ID
    """
    record = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).first()
    if not record:
        return None
    return record
