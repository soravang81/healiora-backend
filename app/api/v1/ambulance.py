from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.schemas.ambulance import AmbulanceCreate, AmbulanceOut, AmbulanceLogin, PasswordChangeRequest, PasswordChangeVerify, AmbulanceUpdate
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

@router.get("/me", response_model=AmbulanceOut)
def get_my_ambulance_profile(
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    ambulance = ambulance_service.get_ambulance_by_credential_id(db, int(current_user.id))
    if not ambulance:
        raise HTTPException(status_code=404, detail="Ambulance profile not found")
    return ambulance

@router.put("/me", response_model=AmbulanceOut)
def update_my_ambulance_profile(
    payload: AmbulanceUpdate,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    ambulance = ambulance_service.get_ambulance_by_credential_id(db, int(current_user.id))
    if not ambulance:
        raise HTTPException(status_code=404, detail="Ambulance profile not found")
    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(ambulance, field, value)
    db.commit()
    db.refresh(ambulance)
    return ambulance

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

@router.get("/{ambulance_id}/status")
def get_ambulance_status(ambulance_id: int, db: Session = Depends(get_db)):
    return ambulance_service.is_ambulance_available(db, ambulance_id)

@router.get("/hospital/{hospital_id}/statuses")
def get_hospital_ambulance_statuses(hospital_id: int, db: Session = Depends(get_db)):
    return {"statuses": ambulance_service.get_hospital_ambulance_statuses(db, hospital_id)}

@router.post("/login", response_model=Token)
def login_ambulance(data: AmbulanceLogin, db: Session = Depends(get_db)):
    ambulance_cred = ambulance_service.authenticate_ambulance(db, data.email, data.password)
    if not ambulance_cred:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user_id=ambulance_cred.id, role="ambulance")
    return {"access_token": token, "token_type": "bearer"}

@router.post("/request-password-change")
def request_password_change_route(
    request: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Request password change for ambulance driver.
    Sends verification code to the user's email (from JWT token).
    """
    if current_user.role != "ambulance":
        raise HTTPException(status_code=403, detail="Only ambulance drivers can change their password")
    
    return ambulance_service.request_password_change(
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
    if current_user.role != "ambulance":
        raise HTTPException(status_code=403, detail="Only ambulance drivers can change their password")
    
    return ambulance_service.change_password_with_verification(
        db, 
        str(current_user.email), 
        request.verification_code
    ) 