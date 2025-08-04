from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.db.models.credential import Credential
from app.services import patient as patient_service
from app.schemas.patient import PatientCreate, PatientOut, PatientUpdate, PatientInitialRegister, PatientCompleteRegister, PatientRegisterResponse
from app.utils.deps import require_admin
from app.schemas.credential import CredentialLogin
from app.schemas.token import Token
from app.core.security import verify_password
from app.utils.jwt import create_access_token
from app.services import credential as credential_service

router = APIRouter(
    # prefix="/patients",
    tags=["Patient"]
)

# ✅ Complete patient registration with automatic login
@router.post("/register-complete", response_model=PatientRegisterResponse, status_code=status.HTTP_201_CREATED)
def complete_patient_registration_with_login(
    data: PatientCompleteRegister,
    db: Session = Depends(get_db)
):
    """
    Complete patient registration with all details and automatic login.
    This endpoint creates the patient profile with all required information
    and returns an access token for immediate login.
    
    Required fields:
    - email: Patient's email address
    - password: Patient's password
    - full_name: Patient's full name
    - age: Patient's age
    - phone_number: Patient's phone number
    - emergency_contact: Emergency contact number
    - gender: Patient's gender
    """
    try:
        result = patient_service.create_complete_patient_with_login(db, data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Initial patient registration (step 1)
@router.post("/register", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def initial_patient_registration(
    data: PatientInitialRegister,
    db: Session = Depends(get_db)
):
    """
    Step 1: Initial patient registration with email, password, and full name.
    Creates credential and basic patient profile.
    """
    try:
        # Convert to PatientCreate format for existing service
        patient_data = PatientCreate(
            email=data.email,
            password=data.password,
            full_name=data.full_name
        )
        patient = patient_service.create_patient_details(db, patient_data)
        
        return patient
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Complete patient profile after registration (step 2 - no auth required)
@router.put("/complete-profile/{patient_id}", response_model=PatientOut)
def complete_patient_profile(
    patient_id: int,
    data: PatientUpdate,
    db: Session = Depends(get_db)
):
    """
    Step 2: Complete patient profile with additional details.
    This endpoint doesn't require authentication - user can complete profile immediately after registration.
    """
    try:
        patient = patient_service.update_patient_by_id(db, patient_id, data)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")
        
        return patient
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Create patient profile (creates both credential and patient)
@router.post("/create", response_model=PatientOut, status_code=status.HTTP_201_CREATED)
def create_patient_profile(
    data: PatientCreate,
    db: Session = Depends(get_db)
):
    try:
        patient = patient_service.create_patient_details(db, data)
        return patient
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=Token)
def login_patient(payload: CredentialLogin, db: Session = Depends(get_db)):
    # Step 1: Fetch credential using email
    credential = credential_service.get_credential_by_email(db, payload.email)
    
    if not credential or not verify_password(payload.password, credential.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Step 2: Get patient profile using credential_id
    patient = patient_service.get_patient_by_credential_id(db, credential.id)
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    
    # Step 3: Generate JWT token with patient role
    token = create_access_token(user_id=credential.id, role="patient")

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# ✅ Update patient profile with additional details (step 2 of registration) - requires auth
@router.put("/update-profile", response_model=PatientOut)
def update_patient_profile(
    data: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Update patient profile with additional details like phone number, age, gender, emergency contact.
    This is step 2 of the registration process.
    """
    try:
        patient = patient_service.update_patient_by_credential_id(db, current_user.id, data)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient profile not found")
        
        return patient
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
