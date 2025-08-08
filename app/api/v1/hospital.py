from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import time

from app.schemas.token import Token
from app.schemas.hospital import HospitalCreate, HospitalOut, HospitalUpdate
from app.schemas.credential import CredentialLogin
from app.db.session import get_db
from app.db.models.credential import Credential as User
from app.db.models.hospital import Hospital
from app.services.hospital import (
    create_hospital_with_credentials,
    get_all_hospitals,
    get_hospital_by_id,
    update_hospital,
    hospital_login,
    get_hospitals_within_10km,
    get_hospitals_within_20km,
)

from app.middleware.auth import get_current_user
from app.utils.deps import require_admin

router = APIRouter(
    # prefix="/hospitals",
    tags=["Hospitals"]
)

# --- Performance Note ---
# FastAPI's Depends is NOT the main cause of slow API responses (700ms+).
# The main causes are usually:
#   - Slow database connection setup (ensure connection pooling is enabled)
#   - Slow database queries (missing indexes, inefficient queries)
#   - Heavy synchronous code blocking the event loop
#   - Cold start of the server or DB
# To profile, we add timing logs below.

def timed_endpoint_sync(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = (time.perf_counter() - start) * 1000
        print(f"⏱️ {func.__name__} took {duration:.2f}ms")
        return result
    return wrapper

# ✅ Admin: Create hospital (credentials + details)
@router.post("/create", response_model=HospitalOut, dependencies=[Depends(require_admin)])
def create_hospital(
    hospital_data: HospitalCreate,
    db: Session = Depends(get_db)
):
    return create_hospital_with_credentials(db=db, hospital_data=hospital_data)


# ✅ Hospital Login
@router.post("/login", response_model=Token)
def login_hospital(payload: CredentialLogin, db: Session = Depends(get_db)):
    token = hospital_login(email=payload.email, password=payload.password, db=db)
    return {
        "access_token": token,
        "token_type": "bearer"
    }

# ✅ Hospital: Get my own hospital details
@router.get("/me", response_model=HospitalOut)
# @timed_endpoint_sync
def get_my_hospital(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "hospital":
        raise HTTPException(status_code=403, detail="Only hospitals can access this endpoint")

    hospital = db.query(Hospital).filter(Hospital.credential_id == current_user.id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    return hospital


# ✅ Public: Get all hospitals
@router.get("/all", response_model=list[HospitalOut])
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


# ✅ Public: Get hospitals within 10km radius
@router.get("/nearby/10km")
def get_hospitals_10km(
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db)
):
    """
    Get hospitals within 10km radius from given coordinates.
    
    Args:
        latitude: User's latitude coordinate
        longitude: User's longitude coordinate
        db: Database session
    
    Returns:
        List of hospitals with distance information, sorted by distance (closest first)
    """
    if not (-90 <= latitude <= 90):
        raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
    if not (-180 <= longitude <= 180):
        raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
    
    hospitals = get_hospitals_within_10km(db, latitude, longitude)
    return {
        "hospitals": hospitals,
        "count": len(hospitals),
        "radius_km": 10,
        "user_location": {"latitude": latitude, "longitude": longitude}
    }


# ✅ Public: Get hospitals within 20km radius
@router.get("/nearby/20km")
def get_hospitals_20km(
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db)
):
    """
    Get hospitals within 20km radius from given coordinates.
    
    Args:
        latitude: User's latitude coordinate
        longitude: User's longitude coordinate
        db: Database session
    
    Returns:
        List of hospitals with distance information, sorted by distance (closest first)
    """
    if not (-90 <= latitude <= 90):
        raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
    if not (-180 <= longitude <= 180):
        raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")
    
    hospitals = get_hospitals_within_20km(db, latitude, longitude)
    return {
        "hospitals": hospitals,
        "count": len(hospitals),
        "radius_km": 20,
        "user_location": {"latitude": latitude, "longitude": longitude}
    }



