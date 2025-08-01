from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.db.models.credential import Credential
from app.services import patient as patient_service
from app.schemas.patient import PatientCreate, PatientOut
from app.utils.deps import require_admin

router = APIRouter(
    # prefix="/patients",
    tags=["Patient"]
)

# ✅ Create patient profile (only once per user)
@router.post("/create", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient_profile(
    data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    try:
        patient = patient_service.create_patient_details(db, current_user.id, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "status": "success",
        "message": "Patient profile created successfully",
        "patient": patient
    }

# ✅ Get your own patient profile
@router.get("/me", response_model=PatientOut)
def get_my_patient_profile(
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    patient = patient_service.get_patient_by_credential_id(db, current_user.id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return patient

# ✅ Admin: Get any patient by ID
@router.get("/{patient_id}", response_model=PatientOut, dependencies=[Depends(require_admin)])
def get_patient_by_id(
    patient_id: int,
    db: Session = Depends(get_db)
):
    patient = patient_service.get_patient_by_credential_id(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient
