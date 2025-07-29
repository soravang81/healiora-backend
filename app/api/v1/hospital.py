from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.hospital import HospitalCreate, HospitalOut
from app.services.hospital import create_hospital, get_hospital_by_id, get_all_hospitals
from app.middleware.auth import get_current_user
from app.db.session import get_db
from app.db.models.user_model import User

router = APIRouter()

# ---------------------------
# Create a Hospital (Admins Only)
# ---------------------------
@router.post("/", response_model=HospitalOut, status_code=status.HTTP_201_CREATED)
def create_hospital_route(
    hospital: HospitalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create hospitals")
    
    return create_hospital(db=db, hospital_data=hospital, user_id=current_user.id)


# ---------------------------
# Get Hospital by ID
# ---------------------------
@router.get("/{hospital_id}", response_model=HospitalOut)
def get_hospital_route(
    hospital_id: int,
    db: Session = Depends(get_db),
):
    db_hospital = get_hospital_by_id(db, hospital_id)
    if not db_hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return db_hospital

# ---------------------------
# Get All Approved Hospitals
# ---------------------------
@router.get("/", response_model=list[HospitalOut])
def list_hospitals(
    db: Session = Depends(get_db),
):
    return get_all_hospitals(db)
