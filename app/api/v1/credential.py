from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.credential import CredentialCreate, CredentialOut
from app.schemas.hospital import HospitalCreate, HospitalOut
from app.services import credential as credential_service
from app.services import hospital as hospital_service
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.utils.deps import require_admin
from app.db.models.credential import Credential
from app.services.credential import create_hospital_by_admin as create_hospital_entry
from app.schemas.credential import CredentialLogin
from app.schemas.patient import PatientCreate
from app.schemas.patient import PatientRegisterSchema


router = APIRouter(
    prefix="/credentials",
    tags=["Credential"]
)

from app.schemas.token import Token
from app.core.security import verify_password
from app.utils.jwt import create_access_token

from app.schemas.credential import CredentialLogin  # You'll create this schema

@router.post("/login", response_model=Token)
def login_user(data: CredentialLogin, db: Session = Depends(get_db)):
    user = credential_service.get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user_id=user.id)

    return {"access_token": token, "token_type": "bearer"}

@router.post("/login-admin", response_model=Token)
def login_admin(data: CredentialLogin, db: Session = Depends(get_db)):
    user = credential_service.get_user_by_email(db, data.email)

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin accounts are allowed to log in")

    token = create_access_token(user_id=user.id)
    return {"access_token": token, "token_type": "bearer"}

# ✅ Public: Register new user credential (default role = "patient")
@router.post("/register", response_model=CredentialOut, status_code=status.HTTP_201_CREATED)
def register_user(data: PatientRegisterSchema, db: Session = Depends(get_db)):
    return credential_service.create_credential(db, data)

# ✅ Logged-in user: Get their own profile
@router.get("/me", response_model=CredentialOut)
def get_my_profile(current_user: Credential = Depends(get_current_user)):
    return current_user

# ✅ Admin: Get any credential by ID
@router.get("/{credential_id}", response_model=CredentialOut, dependencies=[Depends(require_admin)])
def get_user_by_id(credential_id: int, db: Session = Depends(get_db)):
    credential = credential_service.get_credential_by_id(db, credential_id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    return credential

# ✅ Admin: Create hospital (with nested credential)
@router.post("/create-hospital", response_model=HospitalOut)
def create_hospital_by_admin(
    hospital_data: HospitalCreate,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create hospitals")

    # Step 1: Create hospital user credential
    hospital_cred = credential_service.create_credential(db=db, data=hospital_data.credential)

    # Step 2: Create hospital entry
    return create_hospital_entry(db=db, credential_id=hospital_cred.id, hospital_data=hospital_data)
