from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.doctor import DoctorCreate, DoctorOut, DoctorLogin, PasswordChangeRequest, PasswordChangeVerify, DoctorUpdate
from app.db.session import get_db
from app.services import doctor as doctor_service
from app.schemas.token import Token
from app.core.security import verify_password
from app.utils.jwt import create_access_token
from app.db.models.credential import Credential
from app.services.doctor import create_doctor
from app.middleware.auth import get_current_user


router = APIRouter(
    prefix="/doctors",
    tags=["doctors"]
)

@router.get("/me", response_model=DoctorOut)
def get_my_doctor_profile(
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    doctor = doctor_service.get_doctor_by_credential_id(db, int(current_user.id))
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return doctor

@router.put("/me", response_model=DoctorOut)
def update_my_doctor_profile(
    payload: DoctorUpdate,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    doctor = doctor_service.get_doctor_by_credential_id(db, int(current_user.id))
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(doctor, field, value)
    db.commit()
    db.refresh(doctor)
    return doctor

@router.post("/", response_model=DoctorOut, status_code=status.HTTP_201_CREATED)
def create_doctor_route(
    doctor_in: DoctorCreate,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Create a new doctor (hospital user only).
    """
    return create_doctor(db=db, doctor_in=doctor_in, current_user=current_user)



@router.post("/login-doctor", response_model=Token)
def login_doctor(data: DoctorLogin, db: Session = Depends(get_db)):
    # First get the credential by email
    credential = db.query(Credential).filter(Credential.email == data.email).first()
    if not credential or not verify_password(data.password, credential.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Then get the doctor by credential_id
    doctor = doctor_service.get_doctor_by_credential_id(db, credential.id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")

    token = create_access_token(user_id=credential.id, role="doctor")

    return {"access_token": token, "token_type": "bearer"}

@router.get("/", response_model=List[DoctorOut])
def get_all_doctors(db: Session = Depends(get_db)):
    return doctor_service.get_all_doctors(db)

@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor_by_id(doctor_id: int, db: Session = Depends(get_db)):
    doctor = doctor_service.get_doctor_by_id(db, doctor_id)
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor

@router.get("/hospital/{hospital_id}", response_model=List[DoctorOut])
def get_doctors_by_hospital(hospital_id: int, db: Session = Depends(get_db)):
    return doctor_service.get_doctors_by_hospital(db, hospital_id)

@router.get("/{doctor_id}/status")
def get_doctor_status(doctor_id: int, db: Session = Depends(get_db)):
    return doctor_service.is_doctor_available(db, doctor_id)

@router.get("/hospital/{hospital_id}/statuses")
def get_hospital_doctor_statuses(hospital_id: int, db: Session = Depends(get_db)):
    return {"statuses": doctor_service.get_hospital_doctor_statuses(db, hospital_id)}

@router.post("/request-password-change")
def request_password_change_route(
    request: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Request password change for doctor.
    Sends verification code to the user's email (from JWT token).
    """
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can change their password")
    
    return doctor_service.request_password_change(
        db, 
        str(current_user.email), 
        request.current_password, 
        request.new_password
    )

@router.post("/change-password")
def change_password_route(
    request: PasswordChangeVerify,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Change password using verification code.
    """
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can change their password")
    
    return doctor_service.change_password_with_verification(
        db, 
        str(current_user.email), 
        request.verification_code
    )