from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.hospital import Hospital
from app.schemas.hospital import HospitalCreate, HospitalUpdate


def create_hospital(db: Session, hospital_data: HospitalCreate) -> Hospital:
    # Check if user already has a hospital
    existing = db.query(Hospital).filter(Hospital.user_id == hospital_data.user_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hospital already exists for this user."
        )

    hospital = Hospital(**hospital_data.dict())
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital


def get_all_hospitals(db: Session) -> list[Hospital]:
    return db.query(Hospital).all()


def get_approved_hospitals(db: Session) -> list[Hospital]:
    return db.query(Hospital).filter(Hospital.approved == True).all()


def get_pending_hospitals(db: Session) -> list[Hospital]:
    return db.query(Hospital).filter(Hospital.pending == True).all()


def get_hospital_by_id(db: Session, hospital_id: int) -> Hospital:
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital


def update_hospital(db: Session, hospital_id: int, updates: HospitalUpdate) -> Hospital:
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    for field, value in updates.dict(exclude_unset=True).items():
        setattr(hospital, field, value)

    db.commit()
    db.refresh(hospital)
    return hospital
