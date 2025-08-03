from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.credential import Credential
from app.schemas.credential import CredentialLogin, CredentialOut, UserDataResponse, UniversalUserResponse
from app.schemas.token import Token
from app.core.security import verify_password
from app.utils.jwt import create_access_token
from app.services import patient as patient_service
from app.services import doctor as doctor_service
from app.services import ambulance as ambulance_service
from app.middleware.auth import get_current_user

router = APIRouter(
    prefix="/credential",
    tags=["Credential"]
)

@router.post("/login", response_model=Token)
def universal_login(payload: CredentialLogin, db: Session = Depends(get_db)):
    """
    Universal login endpoint for patients, doctors, and ambulances.
    Authenticates user and returns JWT token with appropriate role.
    """
    # Step 1: Find credential by email
    credential = db.query(Credential).filter(Credential.email == payload.email).first()
    
    if not credential or not verify_password(payload.password, credential.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Step 2: Verify the user has a valid role
    valid_roles = ["patient", "doctor", "ambulance", "hospital"]
    if credential.role not in valid_roles:
        raise HTTPException(status_code=403, detail="Invalid user role")
    
    # Step 3: Verify the user profile exists (optional check)
    profile_exists = False
    
    if credential.role == "patient":
        patient = patient_service.get_patient_by_credential_id(db, credential.id)
        profile_exists = patient is not None
    elif credential.role == "doctor":
        doctor = doctor_service.get_doctor_by_credential_id(db, credential.id)
        profile_exists = doctor is not None
    elif credential.role == "ambulance":
        ambulance = ambulance_service.get_ambulance_by_credential_id(db, credential.id)
        profile_exists = ambulance is not None
    elif credential.role == "hospital":
        # For hospital, we can skip profile check as it's handled differently
        profile_exists = True
    
    if not profile_exists:
        raise HTTPException(status_code=404, detail=f"{credential.role.capitalize()} profile not found")
    
    # Step 4: Generate JWT token with user_id and role
    token = create_access_token(user_id=credential.id, role=credential.role)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": credential.role,
        "user_id": credential.id
    }

@router.get("/me", response_model=UniversalUserResponse)
def get_my_complete_profile(
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Universal /me endpoint that returns complete user details based on their role.
    
    Returns:
    - For Patients: full_name, age, gender, phone_number, emergency_contact
    - For Doctors: name, address, education, specialization, years_of_experience
    - For Ambulances: driver_name, driver_phone, ambulance_number, vehicle_type
    
    Also includes profile completion percentage and credential information.
    """
    # Base response with credential information
    response_data = {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "profile_completion_percentage": 0
    }
    
    # Get role-specific profile data
    if current_user.role == "patient":
        patient = patient_service.get_patient_by_credential_id(db, current_user.id)
        if patient:
            response_data.update({
                "full_name": patient.full_name,
                "age": patient.age,
                "gender": patient.gender,
                "phone_number": patient.phone_number,
                "emergency_contact": patient.emergency_contact
            })
            # Calculate profile completion for patient
            filled_fields = sum(1 for field in [patient.full_name, patient.age, patient.gender, 
                                              patient.phone_number, patient.emergency_contact] if field is not None)
            response_data["profile_completion_percentage"] = int((filled_fields / 5) * 100)
    
    elif current_user.role == "doctor":
        doctor = doctor_service.get_doctor_by_credential_id(db, current_user.id)
        if doctor:
            response_data.update({
                "name": doctor.name,
                "address": doctor.address,
                "education": doctor.education,
                "specialization": doctor.specialization,
                "years_of_experience": doctor.years_of_experience
            })
            # Calculate profile completion for doctor
            filled_fields = sum(1 for field in [doctor.name, doctor.address, doctor.education,
                                              doctor.specialization, doctor.years_of_experience] if field is not None)
            response_data["profile_completion_percentage"] = int((filled_fields / 5) * 100)
    
    elif current_user.role == "ambulance":
        ambulance = ambulance_service.get_ambulance_by_credential_id(db, current_user.id)
        if ambulance:
            response_data.update({
                "driver_name": ambulance.driver_name,
                "driver_phone": ambulance.driver_phone,
                "ambulance_number": ambulance.ambulance_number,
                "vehicle_type": ambulance.vehicle_type
            })
            # Calculate profile completion for ambulance
            filled_fields = sum(1 for field in [ambulance.driver_name, ambulance.driver_phone,
                                              ambulance.ambulance_number, ambulance.vehicle_type] if field is not None)
            response_data["profile_completion_percentage"] = int((filled_fields / 4) * 100)
    
    elif current_user.role == "hospital":
        # For hospital, we can add hospital-specific fields if needed
        response_data["profile_completion_percentage"] = 100  # Assume complete for hospital
    
    return UniversalUserResponse(**response_data)

@router.get("/user-data", response_model=UserDataResponse)
def get_user_data(
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Get comprehensive user data including credential and profile information.
    Returns user data with role-specific profile information.
    """
    profile_data = None
    
    # Get role-specific profile data
    if current_user.role == "patient":
        patient = patient_service.get_patient_by_credential_id(db, current_user.id)
        if patient:
            profile_data = {
                "full_name": patient.full_name,
                "gender": patient.gender,
                "phone_number": patient.phone_number,
                "age": patient.age,
                "emergency_contact": patient.emergency_contact
            }
    elif current_user.role == "doctor":
        doctor = doctor_service.get_doctor_by_credential_id(db, current_user.id)
        if doctor:
            profile_data = {
                "name": doctor.name,
                "phone_number": doctor.phone_number,
                "address": doctor.address,
                "education": doctor.education,
                "specialization": doctor.specialization,
                "years_of_experience": doctor.years_of_experience
            }
    elif current_user.role == "ambulance":
        ambulance = ambulance_service.get_ambulance_by_credential_id(db, current_user.id)
        if ambulance:
            profile_data = {
                "driver_name": ambulance.driver_name,
                "driver_phone": ambulance.driver_phone,
                "ambulance_number": ambulance.ambulance_number,
                "vehicle_type": ambulance.vehicle_type
            }
    
    return UserDataResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        profile_data=profile_data
    )


