from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.credential import Credential
from app.db.models.patient import Patient
from app.schemas.patient import PatientOut, PatientUpdate
from app.middleware.auth import get_current_user

router = APIRouter(
    prefix="/patients",
    tags=["patients"],
)

@router.get("/me", response_model=PatientOut)
def get_my_patient_profile(
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user),
):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can access this endpoint")

    patient = db.query(Patient).filter(Patient.credential_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return patient

@router.put("/update-profile", response_model=PatientOut)
def update_my_patient_profile(
    data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user),
):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can update their profile")

    patient = db.query(Patient).filter(Patient.credential_id == current_user.id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)

    db.commit()
    db.refresh(patient)
    return patient
