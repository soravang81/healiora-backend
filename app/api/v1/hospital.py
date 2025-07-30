from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.token import Token
from app.db.session import get_db
from app.schemas.hospital import HospitalCreate, HospitalOut, HospitalUpdate
from app.services.hospital import (
    create_hospital_with_credentials,
    get_all_hospitals,
    get_hospital_by_id,
    update_hospital,
)

from app.middleware.auth import get_current_user
from app.utils.deps import require_admin
from app.schemas.credential import CredentialLogin 
from app.services.hospital import hospital_login

router = APIRouter(
    prefix="/hospitals",
    tags=["Hospitals"]
)

# ✅ Admin: Create hospital (credentials + details)
@router.post("/create", response_model=HospitalOut, dependencies=[Depends(require_admin)])
def create_hospital(
    hospital_data: HospitalCreate,
    db: Session = Depends(get_db)
):
    return create_hospital_with_credentials(db=db, hospital_data=hospital_data)

@router.post("/login", response_model=Token)
def login_hospital(payload: CredentialLogin, db: Session = Depends(get_db)):
    token = hospital_login(email=payload.email, password=payload.password, db=db)
    return {"access_token": token}

# ✅ Public: Get all hospitals
@router.get("/", response_model=list[HospitalOut])
def fetch_all_hospitals(db: Session = Depends(get_db)):
    return get_all_hospitals(db)

# ✅ Public: Get hospital by ID
@router.get("/{hospital_id}", response_model=HospitalOut)
def fetch_hospital_by_id(hospital_id: int, db: Session = Depends(get_db)):
    return get_hospital_by_id(db, hospital_id)

# ✅ Admin: Update hospital
@router.put("/{hospital_id}", response_model=HospitalOut, dependencies=[Depends(require_admin)])
def update_hospital_info(
    hospital_id: int,
    updates: HospitalUpdate,
    db: Session = Depends(get_db)
):
    return update_hospital(db, hospital_id, updates)
