# app/api/v1/patient_assignment.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.utils.deps import get_current_user
from app.db.models.credential import Credential
from app.schemas.patient_assignment import (
    PatientAssignmentCreate,
    PatientAssignmentOut,
    PatientAssignmentUpdate,
    AssignmentStatusUpdate
)
from app.services.patient_assignment import (
    create_patient_assignment,
    get_patient_assignment_by_id,
    get_patient_assignments,
    get_doctor_assignments,
    get_ambulance_assignments,
    get_hospital_assignments,
    get_active_assignments,
    update_assignment_status,
    complete_assignment,
    get_assignment_statistics,
    get_assignment_with_context
)
from app.services.doctor import get_doctor_by_credential_id
from app.services.ambulance import get_ambulance_by_credential_id

router = APIRouter()


@router.post("/assign", response_model=PatientAssignmentOut)
def assign_patient_to_resources(
    assignment: PatientAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Hospital assigns patient to doctor and/or ambulance
    """
    if current_user.role != "hospital":
        raise HTTPException(status_code=403, detail="Access denied. Hospital users only.")
    
    # Verify the hospital ID matches the current user's hospital
    user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
    
    if not user_hospital_id:
        raise HTTPException(status_code=404, detail="Hospital not found for current user")
    
    if assignment.hospital_id != user_hospital_id:
        raise HTTPException(status_code=403, detail="Access denied. Can only assign patients to your own hospital.")
    
    # Validate assignment type
    if assignment.assignment_type not in ["doctor", "ambulance", "both"]:
        raise HTTPException(status_code=400, detail="Invalid assignment type. Must be 'doctor', 'ambulance', or 'both'")
    
    # Validate that required IDs are provided based on assignment type
    if assignment.assignment_type in ["doctor", "both"] and not assignment.doctor_id:
        raise HTTPException(status_code=400, detail="Doctor ID is required for doctor assignments")
    
    if assignment.assignment_type in ["ambulance", "both"] and not assignment.ambulance_id:
        raise HTTPException(status_code=400, detail="Ambulance ID is required for ambulance assignments")
    
    # Validate ID ranges to prevent integer overflow issues
    max_int = 2147483647
    max_bigint = 9223372036854775807
    
    if assignment.sos_request_id and assignment.sos_request_id > max_bigint:
        raise HTTPException(status_code=400, detail="SOS request ID is too large")
    
    if assignment.patient_id and assignment.patient_id > max_int:
        raise HTTPException(status_code=400, detail="Patient ID is too large")
    
    if assignment.doctor_id and assignment.doctor_id > max_int:
        raise HTTPException(status_code=400, detail="Doctor ID is too large")
    
    if assignment.ambulance_id and assignment.ambulance_id > max_int:
        raise HTTPException(status_code=400, detail="Ambulance ID is too large")
    
    if assignment.hospital_id and assignment.hospital_id > max_int:
        raise HTTPException(status_code=400, detail="Hospital ID is too large")
    
    try:
        result = create_patient_assignment(db, assignment)
        return result
    except Exception as e:
        # Log the error for debugging
        print(f"Error creating patient assignment: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create assignment: {str(e)}")


@router.get("/me/assigned-patients", response_model=List[PatientAssignmentOut])
def get_my_assigned_patients_api(
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Return assignments for the current user based on role.
    - doctor: assignments where doctor_id = my doctor.id
    - ambulance: assignments where ambulance_id = my ambulance.id
    - hospital: assignments for my hospital.id
    """
    if current_user.role == "doctor":
        doctor = get_doctor_by_credential_id(db, current_user.id)
        return get_doctor_assignments(db, doctor.id, status, limit, offset)
    elif current_user.role == "ambulance":
        ambulance = get_ambulance_by_credential_id(db, current_user.id)
        return get_ambulance_assignments(db, ambulance.id, status, limit, offset)
    elif current_user.role == "hospital":
        user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
        if not user_hospital_id:
            raise HTTPException(status_code=404, detail="Hospital not found for current user")
        return get_hospital_assignments(db, user_hospital_id, status, limit, offset)
    else:
        raise HTTPException(status_code=403, detail="Access denied for this role.")


@router.get("/patient/{patient_id}", response_model=List[PatientAssignmentOut])
def get_patient_assignments_api(
    patient_id: int,
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Get all assignments for a specific patient
    """
    if current_user.role not in ["hospital", "doctor", "ambulance"]:
        raise HTTPException(status_code=403, detail="Access denied. Hospital, Doctor, or Ambulance users only.")
    
    # Verify access permissions
    if current_user.role == "hospital":
        # Hospital users can see assignments for their hospital
        user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
        if not user_hospital_id:
            raise HTTPException(status_code=404, detail="Hospital not found for current user")
        
        # Check if assignment belongs to their hospital
        assignments = get_patient_assignments(db, patient_id, status, limit, offset)
        hospital_assignments = [a for a in assignments if a.hospital_id == user_hospital_id]
        return hospital_assignments
    
    elif current_user.role == "doctor":
        # Doctor users can see assignments where they are assigned
        assignments = get_patient_assignments(db, patient_id, status, limit, offset)
        doctor_assignments = [a for a in assignments if a.doctor_id == current_user.id]
        return doctor_assignments
    
    elif current_user.role == "ambulance":
        # Ambulance users can see assignments where they are assigned
        assignments = get_patient_assignments(db, patient_id, status, limit, offset)
        ambulance_assignments = [a for a in assignments if a.ambulance_id == current_user.id]
        return ambulance_assignments


@router.get("/doctor/{doctor_id}", response_model=List[PatientAssignmentOut])
def get_doctor_assignments_api(
    doctor_id: int,
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Get all assignments for a specific doctor
    """
    if current_user.role not in ["hospital", "doctor"]:
        raise HTTPException(status_code=403, detail="Access denied. Hospital or Doctor users only.")
    
    # Verify access permissions
    if current_user.role == "doctor":
        if current_user.id != doctor_id:
            raise HTTPException(status_code=403, detail="Access denied. Can only view your own assignments.")
    
    elif current_user.role == "hospital":
        # Hospital users can see assignments for their hospital
        user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
        if not user_hospital_id:
            raise HTTPException(status_code=404, detail="Hospital not found for current user")
        
        # Check if doctor belongs to their hospital
        from app.services.doctor import get_doctor_by_id
        doctor = get_doctor_by_id(db, doctor_id)
        if not doctor or doctor.hospital_id != user_hospital_id:
            raise HTTPException(status_code=403, detail="Access denied. Can only view assignments for doctors in your hospital.")
    
    return get_doctor_assignments(db, doctor_id, status, limit, offset)


@router.get("/ambulance/{ambulance_id}", response_model=List[PatientAssignmentOut])
def get_ambulance_assignments_api(
    ambulance_id: int,
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Get all assignments for a specific ambulance
    """
    if current_user.role not in ["hospital", "ambulance"]:
        raise HTTPException(status_code=403, detail="Access denied. Hospital or Ambulance users only.")
    
    # Verify access permissions
    if current_user.role == "ambulance":
        if current_user.id != ambulance_id:
            raise HTTPException(status_code=403, detail="Access denied. Can only view your own assignments.")
    
    elif current_user.role == "hospital":
        # Hospital users can see assignments for their hospital
        user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
        if not user_hospital_id:
            raise HTTPException(status_code=404, detail="Hospital not found for current user")
        
        # Check if ambulance belongs to their hospital
        from app.services.ambulance import get_ambulance_by_id
        ambulance = get_ambulance_by_id(db, ambulance_id)
        if not ambulance or ambulance.hospital_id != user_hospital_id:
            raise HTTPException(status_code=403, detail="Access denied. Can only view assignments for doctors in your hospital.")
    
    return get_ambulance_assignments(db, ambulance_id, status, limit, offset)


@router.get("/hospital/{hospital_id}", response_model=List[PatientAssignmentOut])
def get_hospital_assignments_api(
    hospital_id: int,
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Get all assignments for a specific hospital
    """
    if current_user.role != "hospital":
        raise HTTPException(status_code=403, detail="Access denied. Hospital users only.")
    
    # Verify the hospital ID matches the current user's hospital
    user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
    
    if not user_hospital_id:
        raise HTTPException(status_code=404, detail="Hospital not found for current user")
    
    if hospital_id != user_hospital_id:
        raise HTTPException(status_code=403, detail="Access denied. Can only view assignments for your own hospital.")
    
    return get_hospital_assignments(db, hospital_id, status, limit, offset)


@router.get("/active", response_model=List[PatientAssignmentOut])
def get_active_assignments_api(
    hospital_id: Optional[int] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Get all active assignments
    """
    if current_user.role not in ["hospital", "doctor", "ambulance"]:
        raise HTTPException(status_code=403, detail="Access denied. Hospital, Doctor, or Ambulance users only.")
    
    # Filter by hospital if user is hospital
    if current_user.role == "hospital":
        user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
        if not user_hospital_id:
            raise HTTPException(status_code=404, detail="Hospital not found for current user")
        hospital_id = user_hospital_id
    
    return get_active_assignments(db, hospital_id, limit, offset)


@router.put("/{assignment_id}/status", response_model=PatientAssignmentOut)
def update_assignment_status_api(
    assignment_id: int,
    status_update: AssignmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Update assignment status and notes
    """
    if current_user.role not in ["hospital", "doctor", "ambulance"]:
        raise HTTPException(status_code=403, detail="Access denied. Hospital, Doctor, or Ambulance users only.")
    
    # Get the assignment
    assignment = get_patient_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Verify access permissions
    if current_user.role == "hospital":
        user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
        if not user_hospital_id or assignment.hospital_id != user_hospital_id:
            raise HTTPException(status_code=403, detail="Access denied. Can only update assignments for your hospital.")
    
    elif current_user.role == "doctor":
        if not assignment.doctor_id or assignment.doctor_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied. Can only update assignments where you are assigned.")
    
    elif current_user.role == "ambulance":
        if not assignment.ambulance_id or assignment.ambulance_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied. Can only update assignments where you are assigned.")
    
    try:
        result = update_assignment_status(db, assignment_id, status_update)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update assignment: {str(e)}")


@router.post("/{assignment_id}/complete", response_model=PatientAssignmentOut)
def complete_assignment_api(
    assignment_id: int,
    completion_notes: str,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Mark assignment as completed
    """
    if current_user.role not in ["hospital", "doctor", "ambulance"]:
        raise HTTPException(status_code=403, detail="Access denied. Hospital, Doctor, or Ambulance users only.")
    
    # Get the assignment
    assignment = get_patient_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Verify access permissions
    if current_user.role == "hospital":
        user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
        if not user_hospital_id or assignment.hospital_id != user_hospital_id:
            raise HTTPException(status_code=403, detail="Access denied. Can only complete assignments for your hospital.")
    
    elif current_user.role == "doctor":
        if not assignment.doctor_id or assignment.doctor_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied. Can only complete assignments where you are assigned.")
    
    elif current_user.role == "ambulance":
        if not assignment.ambulance_id or assignment.ambulance_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied. Can only complete assignments where you are assigned.")
    
    try:
        result = complete_assignment(db, assignment_id, completion_notes, current_user.role)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete assignment: {str(e)}")


@router.get("/{assignment_id}/context")
def get_assignment_with_context_api(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Get assignment with additional patient, doctor, ambulance, and hospital context
    """
    if current_user.role not in ["hospital", "doctor", "ambulance"]:
        raise HTTPException(status_code=403, detail="Access denied. Hospital, Doctor, or Ambulance users only.")
    
    # Get the assignment
    assignment = get_patient_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Verify access permissions
    if current_user.role == "hospital":
        user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
        if not user_hospital_id or assignment.hospital_id != user_hospital_id:
            raise HTTPException(status_code=403, detail="Access denied. Can only view assignments for your hospital.")
    
    elif current_user.role == "doctor":
        if not assignment.doctor_id or assignment.doctor_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied. Can only view assignments where you are assigned.")
    
    elif current_user.role == "ambulance":
        if not assignment.ambulance_id or assignment.ambulance_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied. Can only view assignments where you are assigned.")
    
    try:
        result = get_assignment_with_context(db, assignment_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get assignment context: {str(e)}")


@router.get("/statistics")
def get_assignment_statistics_api(
    hospital_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Get assignment statistics
    """
    if current_user.role not in ["hospital", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied. Hospital or Admin users only.")
    
    # Filter by hospital if user is hospital
    if current_user.role == "hospital":
        user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
        if not user_hospital_id:
            raise HTTPException(status_code=404, detail="Hospital not found for current user")
        hospital_id = user_hospital_id
    
    try:
        result = get_assignment_statistics(db, hospital_id, start_date, end_date)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")
