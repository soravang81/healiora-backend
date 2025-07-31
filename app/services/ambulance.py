from sqlalchemy.orm import Session
from app.db.models.ambulance import Ambulance
from app.db.models.credential import Credential
from app.db.models.hospital import Hospital
from app.schemas.ambulance import AmbulanceCreate
from app.core.security import hash_password, verify_password
from app.utils.email import send_email
import secrets
import string
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

def create_ambulance(
    db: Session,
    ambulance_in: AmbulanceCreate,
    current_user: Credential
):
    if current_user.role != "hospital":
        raise HTTPException(status_code=403, detail="Only hospital users can create ambulances")

    # Get hospital row using current_user.id
    hospital = db.query(Hospital).filter(Hospital.credential_id == current_user.id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found for current user")

    # Check if ambulance number already exists
    existing_ambulance = db.query(Ambulance).filter(Ambulance.ambulance_number == ambulance_in.ambulance_number).first()
    if existing_ambulance:
        raise HTTPException(status_code=400, detail="Ambulance with this number already exists")

    # 1. Generate password
    password = generate_password()
    hashed_password = hash_password(password)

    # 2. Create ambulance driver credential
    credential = Credential(
        email=ambulance_in.driver_email,
        password=hashed_password,
        phone_number=ambulance_in.driver_phone,
        role="ambulance",
        is_active=True
    )
    db.add(credential)
    db.commit()
    db.refresh(credential)

    # 3. Create ambulance
    ambulance = Ambulance(
        ambulance_number=ambulance_in.ambulance_number,
        driver_name=ambulance_in.driver_name,
        driver_phone=ambulance_in.driver_phone,
        driver_email=ambulance_in.driver_email,
        vehicle_type=ambulance_in.vehicle_type,
        hospital_id=hospital.id,
        credential_id=credential.id
    )
    db.add(ambulance)
    db.commit()
    db.refresh(ambulance)

    # 4. Email credentials
    send_email(
        to_email=ambulance_in.driver_email,
        subject="Your Ambulance Driver Account Credentials",
        body=f"Welcome to Healiora. Your temporary password is: {password}"
    )

    return ambulance

def get_ambulance_by_id(db: Session, ambulance_id: int):
    return db.query(Ambulance).filter(Ambulance.id == ambulance_id).first()

def get_ambulance_by_email(db: Session, email: str):
    return db.query(Ambulance).filter(Ambulance.driver_email == email).first()

def get_ambulances_by_hospital(db: Session, hospital_id: int):
    return db.query(Ambulance).filter(Ambulance.hospital_id == hospital_id).all()

def get_all_ambulances(db: Session):
    return db.query(Ambulance).all()

def authenticate_ambulance(db: Session, email: str, password: str):
    cred = db.query(Credential).filter(Credential.email == email, Credential.role == "ambulance").first()
    if not cred or not verify_password(password, cred.password):
        return None
    return cred 