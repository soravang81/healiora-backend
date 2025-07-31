from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.hospital import Hospital
from app.db.models.credential import Credential
from app.schemas.hospital import HospitalCreate, HospitalUpdate
from app.core.security import hash_password
from app.utils.jwt import create_access_token
from app.core.security import verify_password


def create_hospital_with_credentials(db: Session, hospital_data: HospitalCreate) -> Hospital:
    # 1. Check if email already exists
    existing = db.query(Credential).filter(Credential.email == hospital_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Create hospital credentials
    credentials = Credential(
        email=hospital_data.email,
        password=hash_password(hospital_data.password),
        role="hospital"  # Just a plain string, no enum
    )
    db.add(credentials)
    db.commit()
    db.refresh(credentials)

    # 3. Create hospital details
    hospital = Hospital(
         credential_id=credentials.id,
         email=hospital_data.email,
        name=hospital_data.name,
        address=hospital_data.address,
        admin_name=hospital_data.admin_name,
        phone=hospital_data.phone,
        latitude=hospital_data.latitude,
        longitude=hospital_data.longitude,
    )
    db.add(hospital)
    db.commit()
    db.refresh(hospital)

    return hospital

def hospital_login(email: str, password: str, db: Session):
    user = db.query(Credential).filter(Credential.email == email).first()

    if not user:
        print("User not found")
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    if not verify_password(password, user.password):
        print("Password verification failed")
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    print(f"User role: {user.role}")  # ✅ This will log the role to the console
    
    if user.role != "hospital":
        raise HTTPException(status_code=403, detail="Only hospital accounts are allowed to log in")

    return create_access_token(user_id=user.id)




def get_all_hospitals(db: Session) -> list[Hospital]:
    return db.query(Hospital).all()


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
