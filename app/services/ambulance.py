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
import random
import time
from app.db.models.patient_assignment import PatientAssignment

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

def get_ambulance_by_id(db: Session, ambulance_id: int) -> Ambulance:
    """
    Get ambulance by ID
    """
    ambulance = db.query(Ambulance).filter(Ambulance.id == ambulance_id).first()
    if not ambulance:
        raise HTTPException(
            status_code=404,
            detail="Ambulance not found with the given ID.",
        )
    return ambulance

def get_ambulance_by_email(db: Session, email: str):
    return db.query(Ambulance).filter(Ambulance.driver_email == email).first()

def get_ambulance_by_credential_id(
    db: Session, credential_id: int
) -> Ambulance:
    """
    Get ambulance by credential ID
    """
    ambulance = db.query(Ambulance).filter(Ambulance.credential_id == credential_id).first()
    if not ambulance:
        raise HTTPException(
            status_code=404,
            detail="Ambulance not found.",
        )
    return ambulance

def get_ambulances_by_hospital(db: Session, hospital_id: int):
    return db.query(Ambulance).filter(Ambulance.hospital_id == hospital_id).all()

def get_all_ambulances(db: Session):
    return db.query(Ambulance).all()

def authenticate_ambulance(db: Session, email: str, password: str):
    cred = db.query(Credential).filter(Credential.email == email, Credential.role == "ambulance").first()
    if not cred or not verify_password(password, cred.password):
        return None
    return cred 

def is_ambulance_available(db: Session, ambulance_id: int) -> dict:
    """Compute ambulance availability from active assignments."""
    active = (
        db.query(PatientAssignment)
        .filter(PatientAssignment.ambulance_id == ambulance_id)
        .filter(PatientAssignment.status.in_(["active"]))
        .filter(PatientAssignment.case_status.in_(["open", "in_progress"]))
        .filter(PatientAssignment.ambulance_assignment_status.in_(["accepted", "en_route"]))
        .order_by(PatientAssignment.created_at.desc())
        .first()
    )
    return {"available": active is None, "active_assignment_id": active.id if active else None}

def get_hospital_ambulance_statuses(db: Session, hospital_id: int) -> list:
    ambulances = get_ambulances_by_hospital(db, hospital_id)
    results = []
    for amb in ambulances:
        s = is_ambulance_available(db, amb.id)
        results.append({"ambulance_id": amb.id, **s})
    return results

def request_password_change(db: Session, email: str, current_password: str, new_password: str):
    """Request password change for ambulance user."""
    # Check if ambulance exists
    ambulance = db.query(Ambulance).filter(Ambulance.driver_email == email).first()
    if not ambulance:
        raise HTTPException(status_code=404, detail="Ambulance not found")
    
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
    Hello {ambulance.driver_name},
    
    You have requested to change your password for your ambulance driver account.
    
    Your verification code is: {verification_code}
    
    This code will expire in 10 minutes.
    
    If you didn't request this password change, please ignore this email.
    
    Best regards,
    Healiora Team
    """
    
    try:
        send_email(
            to_email=email,
            subject="Password Change Request - Ambulance Driver",
            body=email_body
        )
        return {"message": "Verification code sent to your email"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send verification email")

def change_password_with_verification(db: Session, email: str, verification_code: str):
    """Change password using verification code."""
    # Check if ambulance exists
    ambulance = db.query(Ambulance).filter(Ambulance.driver_email == email).first()
    if not ambulance:
        raise HTTPException(status_code=404, detail="Ambulance not found")
    
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