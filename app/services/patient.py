from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db.models.patient import Patient
from app.db.models.credential import Credential
from app.schemas.patient import PatientCreate, PatientUpdate
from app.core.security import hash_password, verify_password
from app.utils.jwt import create_access_token



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


def patient_login(db: Session, email: str, password: str):
    # Step 1: Fetch credential using email
    credential = db.query(Credential).filter(Credential.email == email).first()

    if not credential or not verify_password(password, credential.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Step 2: Fetch patient using credential.id
    patient = db.query(Patient).filter(Patient.credential_id == credential.id).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )

    # Step 3: Generate token with patient role
    token = create_access_token(user_id=credential.id, role="patient")

    # Step 4: Return access token
    return {
        "access_token": token,
        "token_type": "bearer"
    }


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



def update_patient_by_user_id(db: Session, user_id: int, data: PatientUpdate, credentials_id: int) -> Patient:
    patient = db.query(Patient).filter(Patient.credential_id == credentials_id).first()
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

def update_patient_by_id(db: Session, patient_id: int, data: PatientUpdate) -> Patient:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return None

    for key, value in data.dict(exclude_unset=True).items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)
    return patient


def update_patient_by_credential_id(db: Session, credential_id: int, data: PatientUpdate):
    patient = db.query(Patient).filter(Patient.credential_id == credential_id).first()
    if not patient:
        return None

    for key, value in data.dict(exclude_unset=True).items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)
    return patient

