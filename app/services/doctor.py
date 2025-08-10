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
import random
import time

# In-memory storage for verification codes (in production, use Redis or database)
verification_codes = {}

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
        

def generate_verification_code() -> str:
    """Generate a 6-digit verification code."""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def store_verification_code(email: str, code: str, new_password: str = None):
    """Store verification code with expiration (10 minutes)."""
    verification_codes[email] = {
        'code': code,
        'expires_at': time.time() + 600  # 10 minutes
    }
    if new_password:
        verification_codes[email]['new_password'] = new_password

def verify_verification_code(email: str, code: str) -> bool:
    """Verify the provided code for the email."""
    if email not in verification_codes:
        return False
    
    stored_data = verification_codes[email]
    if time.time() > stored_data['expires_at']:
        # Code expired, remove it
        del verification_codes[email]
        return False
    
    if stored_data['code'] == code:
        # Code verified, but don't delete it yet - we need to retrieve the new password
        return True
    
    return False


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

def get_doctor_by_credential_id(db: Session, credential_id: int):
    return db.query(Doctor).filter(Doctor.credential_id == credential_id).first()

def get_doctors_by_hospital(db: Session, hospital_id: int):
    return db.query(Doctor).filter(Doctor.hospital_id == hospital_id).all()

def get_all_doctors(db: Session):
    return db.query(Doctor).all()

def request_password_change(db: Session, email: str, current_password: str, new_password: str):
    """Request password change for doctor user."""
    # Check if doctor exists
    doctor = db.query(Doctor).filter(Doctor.email == email).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check if credential exists
    credential = db.query(Credential).filter(Credential.email == email).first()
    if not credential:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not verify_password(current_password, credential.password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Generate verification code
    verification_code = generate_verification_code()
    store_verification_code(email, verification_code, new_password)
    
    # Send email with verification code
    email_body = f"""
    Hello Dr. {doctor.name},
    
    You have requested to change your password for your doctor account.
    
    Your verification code is: {verification_code}
    
    This code will expire in 10 minutes.
    
    If you didn't request this password change, please ignore this email.
    
    Best regards,
    Healiora Team
    """
    
    try:
        send_email(
            to_email=email,
            subject="Password Change Request - Doctor",
            body=email_body
        )
        return {"message": "Verification code sent to your email"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send verification email")

def change_password_with_verification(db: Session, email: str, verification_code: str):
    """Change password using verification code."""
    # Check if doctor exists
    doctor = db.query(Doctor).filter(Doctor.email == email).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    # Check if credential exists
    credential = db.query(Credential).filter(Credential.email == email).first()
    if not credential:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify the code
    if not verify_verification_code(email, verification_code):
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    
    # Get the stored new password
    if email not in verification_codes or 'new_password' not in verification_codes[email]:
        raise HTTPException(status_code=400, detail="Password change request not found or expired")
    
    new_password = verification_codes[email]['new_password']
    
    # Update password
    credential.password = hash_password(new_password)
    db.commit()
    db.refresh(credential)
    
    # Clean up stored data after successful password change
    if email in verification_codes:
        del verification_codes[email]
    
    return {"message": "Password changed successfully"}