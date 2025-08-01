from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.credential import Credential
from app.db.models.hospital import Hospital
from app.schemas.credential import CredentialCreate
from app.schemas.hospital import HospitalCreate
from app.core.security import hash_password
from app.schemas.patient import PatientRegisterSchema
from app.db.models.patient import Patient
from app.db.models.credential import Credential
from app.schemas.patient import PatientCreate


def create_credential(db: Session, data: PatientRegisterSchema) -> Credential:
    existing = db.query(Credential).filter(Credential.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_cred = Credential(
        email=data.email,
        password=hash_password(data.password),
        phone_number=data.phone_number,
        role=data.role,
    )
    db.add(new_cred)
    db.flush()

    patient = Patient(
        credential_id=new_cred.id,
        username=data.username,
        age=data.age,
        emergency_contact=data.emergency_contact
    )
    db.add(patient)
    db.commit()
    db.refresh(new_cred)
    return new_cred


def get_credential_by_email(db: Session, email: str) -> Credential | None:
    return db.query(Credential).filter(Credential.email == email).first()


def get_credential_by_id(db: Session, credential_id: int) -> Credential | None:
    return db.query(Credential).filter(Credential.id == credential_id).first()


def create_hospital_by_admin(
    db: Session, credential_id: int, hospital_data: HospitalCreate
) -> Hospital:
    # Check if hospital already exists
    existing = db.query(Hospital).filter(Hospital.credential_id == credential_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Hospital already exists for this credential")

    hospital = Hospital(**hospital_data.dict(), credential_id=credential_id)
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital

def get_user_by_email(db: Session, email: str) -> Credential:
    return db.query(Credential).filter(Credential.email == email).first()

