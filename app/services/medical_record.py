from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.medical_records import MedicalRecord
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate

def create_medical_record(db: Session, user_id: int, record_data: MedicalRecordCreate):
    # Check if user already has a medical record
    existing_record = db.query(MedicalRecord).filter(MedicalRecord.user_id == user_id).first()
    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medical record already exists for this user"
        )
    
    new_record = MedicalRecord(user_id=user_id, **record_data.dict())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

def get_medical_record(db: Session, user_id: int):
    record = db.query(MedicalRecord).filter(MedicalRecord.user_id == user_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )
    return record

def update_medical_record(db: Session, user_id: int, update_data: MedicalRecordUpdate):
    record = db.query(MedicalRecord).filter(MedicalRecord.user_id == user_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )
    
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(record, key, value)

    db.commit()
    db.refresh(record)
    return record

def delete_medical_record(db: Session, user_id: int):
    record = db.query(MedicalRecord).filter(MedicalRecord.user_id == user_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medical record not found"
        )
    
    db.delete(record)
    db.commit()
    return {"detail": "Medical record deleted successfully"}
