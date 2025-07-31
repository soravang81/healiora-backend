from sqlalchemy.orm import Session
from app.db.models.doctor import Doctor
from app.db.models.credential import Credential
from app.schemas.doctor import DoctorCreate
from app.core.security import hash_password
from app.utils.email import send_email  # You may need to implement this
import secrets
import string
from app.core.security import verify_password
from app.middleware.auth import get_current_user
from app.db.models.hospital import Hospital
from fastapi import HTTPException

def generate_password(length: int = 12) -> str:
    """Generate a secure random password with letters, digits, and symbols."""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        # Ensure password has at least one lowercase, one uppercase, one digit, and one symbol
        if (any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and any(c.isdigit() for c in password)
            and any(c in string.punctuation for c in password)):
            return password
        

def create_doctor(
    db: Session,
    doctor_in: DoctorCreate,
    current_user: Credential  # Already injected via Depends in route
):
    if current_user.role != "hospital":
        raise HTTPException(status_code=403, detail="Only hospital users can create doctors")

    # Get hospital row using current_user.id
    hospital = db.query(Hospital).filter(Hospital.credential_id == current_user.id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found for current user")

    # 1. Generate password
    password = generate_password()
    hashed_password = hash_password(password)

    # 2. Create doctor credential
    credential = Credential(
        email=doctor_in.email,
        password=hashed_password,
        phone_number=doctor_in.phone_number,
        role="doctor",
        is_active=True
    )
    db.add(credential)
    db.commit()
    db.refresh(credential)

    # 3. Create doctor
    doctor = Doctor(
        name=doctor_in.name,
        phone_number=doctor_in.phone_number,
        email=doctor_in.email,
        address=doctor_in.address,
        education=doctor_in.education,
        specialization=doctor_in.specialization,
        years_of_experience=doctor_in.years_of_experience,
        hospital_id=hospital.id,
        credential_id=credential.id
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)

    # 4. Email credentials
    send_email(
        to_email=doctor_in.email,
        subject="Your Doctor Account Credentials",
        body=f"Welcome to Healiora. Your temporary password is: {password}"
    )

    return doctor

def get_doctor_by_id(db: Session, doctor_id: int):
    return db.query(Doctor).filter(Doctor.id == doctor_id).first()

def get_doctor_by_email(db: Session, email: str):
    return db.query(Doctor).filter(Doctor.email == email).first()

def get_doctors_by_hospital(db: Session, hospital_id: int):
    return db.query(Doctor).filter(Doctor.hospital_id == hospital_id).all()

def get_all_doctors(db: Session):
    return db.query(Doctor).all()