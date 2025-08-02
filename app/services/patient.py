from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models.patient import Patient
from app.db.models.credential import Credential
from app.schemas.patient import PatientCreate, PatientUpdate
from app.core.security import hash_password


def create_patient_details(
    db: Session, data: PatientCreate
) -> Patient:
    # Check if email already exists in credentials
    existing_credential = db.query(Credential).filter(Credential.email == data.email).first()
    if existing_credential:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered.",
        )

    # Create credential first
    credential = Credential(
        email=data.email,
        password=hash_password(data.password),
        role="patient",
    )
    db.add(credential)
    db.flush()  # Get the credential ID without committing

    # Create patient profile
    patient = Patient(
        credential_id=credential.id,
        full_name=data.full_name,
        email=data.email,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


def get_patient_by_credential_id(
    db: Session, credential_id: int
) -> Patient:
    patient = db.query(Patient).filter(Patient.credential_id == credential_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found.",
        )
    return patient



def update_patient_by_user_id(db: Session, user_id: int, data: PatientUpdate):
    patient = db.query(Patient).filter(Patient.credential_id == user_id).first()
    if not patient:
        return None

    for key, value in data.dict(exclude_unset=True).items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)
    return patient


def send_sos(
    db: Session, credential_id: int, data: PatientCreate
) -> Patient:
    # Ensure only one patient profile per credential
    existing = db.query(Patient).filter(Patient.credential_id == credential_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient profile already exists.",
        )

    patient = Patient(**data.dict(), credential_id=credential_id)
    db.add(patient)
    db.commit() 
    db.refresh(patient)
    return patient

def get_patient_by_email(
    db: Session, email: str
) -> Patient:
    patient = db.query(Patient).filter(Patient.email == email).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found with the given email.",
        )
    return patient
