from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.ambulance import AmbulanceCreate, AmbulanceOut, AmbulanceLogin
from app.services import ambulance as ambulance_service
from app.db.session import get_db
from app.schemas.token import Token
from app.core.security import verify_password
from app.utils.jwt import create_access_token
from app.middleware.auth import get_current_user
from app.db.models.credential import Credential

router = APIRouter(
    prefix="/ambulances",
    tags=["ambulances"]
)

@router.post("/", response_model=AmbulanceOut, status_code=status.HTTP_201_CREATED)
def create_ambulance(
    ambulance_in: AmbulanceCreate,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    # Check if ambulance with this email already exists
    existing = ambulance_service.get_ambulance_by_email(db, ambulance_in.driver_email)
    if existing:
        raise HTTPException(status_code=400, detail="Ambulance driver with this email already exists.")
    return ambulance_service.create_ambulance(db, ambulance_in, current_user)

@router.get("/", response_model=List[AmbulanceOut])
def get_all_ambulances(db: Session = Depends(get_db)):
    return ambulance_service.get_all_ambulances(db)

@router.get("/{ambulance_id}", response_model=AmbulanceOut)
def get_ambulance_by_id(ambulance_id: int, db: Session = Depends(get_db)):
    ambulance = ambulance_service.get_ambulance_by_id(db, ambulance_id)
    if not ambulance:
        raise HTTPException(status_code=404, detail="Ambulance not found")
    return ambulance

@router.get("/hospital/{hospital_id}", response_model=List[AmbulanceOut])
def get_ambulances_by_hospital(hospital_id: int, db: Session = Depends(get_db)):
    return ambulance_service.get_ambulances_by_hospital(db, hospital_id)

@router.post("/login", response_model=Token)
def login_ambulance(data: AmbulanceLogin, db: Session = Depends(get_db)):
    ambulance_cred = ambulance_service.authenticate_ambulance(db, data.email, data.password)
    if not ambulance_cred:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user_id=ambulance_cred.id, role="ambulance")
    return {"access_token": token, "token_type": "bearer"} 