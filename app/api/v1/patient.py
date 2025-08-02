from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.db.models.credential import Credential
from app.services import patient as patient_service
from app.schemas.patient import PatientCreate, PatientOut
from app.utils.deps import require_admin
from app.schemas.token import Token
from app.schemas.credential import CredentialLogin
from app.schemas.patient import PatientLogin, PatientUpdate
from app.core.security import verify_password
from app.utils.jwt import create_access_token
from app.middleware.auth import get_current_user as get_current_user_id




router = APIRouter(
    # prefix="/patients",
    tags=["Patient"]
)

# ✅ Create patient profile (only once per user)
@router.post("/create", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient_profile(
    data: PatientCreate,
    db: Session = Depends(get_db),
):
    try:
        patient = patient_service.create_patient_details(db, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return patient  # ✅ Matches PatientOut


@router.post("/login-doctor", response_model=Token)
def login_doctor(data: PatientLogin, db: Session = Depends(get_db)):
    patient = patient_service.get_patient_by_email(db, data.email)
    if not patient or not verify_password(data.password, patient.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user_id=patient.id)

    return {"access_token": token, "token_type": "bearer"}

@router.put("/update", response_model=PatientOut)
def update_own_patient_profile(
    data: PatientUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id)
):
    patient = patient_service.update_patient_by_user_id(db, user_id, data)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient



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
