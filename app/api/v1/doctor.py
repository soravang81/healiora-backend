from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.doctor import DoctorCreate, DoctorOut, DoctorLogin
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
    doctor = doctor_service.get_doctor_by_email(db, data.email)
    if not doctor or not verify_password(data.password, doctor.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user_id=user.id)

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