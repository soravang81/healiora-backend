from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordOut
from app.services import medical_record
from app.middleware.auth import get_current_user
from app.db.models.credential import Credential as User  # Assuming Credential is used for user authentication

router = APIRouter(
    prefix="/medical-records",
    tags=["Medical Records"]
)

@router.post("/", response_model=MedicalRecordOut, status_code=status.HTTP_201_CREATED)
def create_medical_record(
    data: MedicalRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return medical_record.create_medical_record(db, user_id=current_user.id, record_data=data)

@router.get("/", response_model=MedicalRecordOut)
def get_medical_record(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return medical_record.get_medical_record(db, user_id=current_user.id)

@router.put("/", response_model=MedicalRecordOut)
def update_medical_record(
    data: MedicalRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return medical_record.update_medical_record(db, user_id=current_user.id, update_data=data)

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_medical_record(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    medical_record.delete_medical_record(db, user_id=current_user.id)
    return
