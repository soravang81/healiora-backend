from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.db.models.hospital import Hospital
from app.db.models.credential import Credential
from app.schemas.hospital import HospitalCreate, HospitalUpdate
from app.core.security import hash_password
from app.utils.jwt import create_access_token
from app.core.security import verify_password
from fastapi import status
import math


def create_hospital_with_credentials(db: Session, hospital_data: HospitalCreate) -> Hospital:
    # 1. Check if email already exists
    existing = db.query(Credential).filter(Credential.email == hospital_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2. Create hospital credentials
    credentials = Credential(
        email=hospital_data.email,
        password=hash_password(hospital_data.password),
        role="hospital"  # Just a plain string, no enum
    )
    db.add(credentials)
    db.commit()
    db.refresh(credentials)

    # 3. Create hospital details
    hospital = Hospital(
        credential_id=credentials.id,
        email=hospital_data.email,
        name=hospital_data.name,
        address=hospital_data.address,
        phone=hospital_data.phone,
        admin_name=hospital_data.admin_name,
        latitude=hospital_data.latitude,
        longitude=hospital_data.longitude,
        hospital_type=hospital_data.hospital_type,
        emergency_available=hospital_data.emergency_available,
        available_24_7=hospital_data.available_24_7,
        registration_number=hospital_data.registration_number,
        departments=hospital_data.departments,
    )
    db.add(hospital)
    db.commit()
    db.refresh(hospital)

    return hospital

def hospital_login(email: str, password: str, db: Session) -> str:
    user = db.query(Credential).filter(Credential.email == email).first()
    
    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if user.role != "hospital":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hospital accounts can access this endpoint"
        )
    
    token = create_access_token(user_id=user.id, role=user.role)
    return token


def get_all_hospitals(db: Session) -> list[Hospital]:
    return db.query(Hospital).all()


def get_hospital_by_id(db: Session, hospital_id: int) -> Hospital:
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital


def update_hospital(db: Session, hospital_id: int, updates: HospitalUpdate) -> Hospital:
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    for field, value in updates.dict(exclude_unset=True).items():
        setattr(hospital, field, value)

    db.commit()
    db.refresh(hospital)
    return hospital


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two points using the Haversine formula.
    Returns distance in kilometers.
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r

def get_hospitals_within_radius(db: Session, user_lat: float, user_lon: float, radius_km: float) -> list[dict]:
    """
    Get hospitals within a specified radius from given coordinates.
    Returns list of hospitals with distance information.
    """
    hospitals = db.query(Hospital).filter(
        Hospital.latitude.isnot(None),
        Hospital.longitude.isnot(None)
    ).all()
    
    nearby_hospitals = []
    
    for hospital in hospitals:
        distance = calculate_distance(user_lat, user_lon, hospital.latitude, hospital.longitude)
        
        if distance <= radius_km:
            hospital_dict = {
                "id": hospital.id,
                "name": hospital.name,
                "address": hospital.address,
                "latitude": hospital.latitude,
                "longitude": hospital.longitude,
                "phone": hospital.phone,
                "email": hospital.email,
                "admin_name": hospital.admin_name,
                "distance_km": round(distance, 2),
                "hospital_type": hospital.hospital_type,
                "emergency_available": hospital.emergency_available,
                "available_24_7": hospital.available_24_7,
                "registration_number": hospital.registration_number,
                "departments": hospital.departments
            }
            nearby_hospitals.append(hospital_dict)
    
    # Sort by distance (closest first)
    nearby_hospitals.sort(key=lambda x: x["distance_km"])
    
    return nearby_hospitals

def get_hospitals_within_10km(db: Session, user_lat: float, user_lon: float) -> list[dict]:
    """Get hospitals within 10km radius"""
    return get_hospitals_within_radius(db, user_lat, user_lon, 10.0)

def get_hospitals_within_20km(db: Session, user_lat: float, user_lon: float) -> list[dict]:
    """Get hospitals within 20km radius"""
    return get_hospitals_within_radius(db, user_lat, user_lon, 20.0)


