# app/services/patient_assignment.py
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from app.db.models.patient_assignment import PatientAssignment
from app.db.models.patient import Patient
from app.db.models.doctor import Doctor
from app.db.models.ambulance import Ambulance
from app.db.models.hospital import Hospital
from app.db.models.medical_records import MedicalRecord
from app.db.models.socket_log import SocketLog
from app.schemas.patient_assignment import PatientAssignmentCreate, PatientAssignmentUpdate


def create_patient_assignment(db: Session, assignment_data: PatientAssignmentCreate) -> PatientAssignment:
    """
    Create a new patient assignment
    """
    # Validate assignment type
    if assignment_data.assignment_type not in ["doctor", "ambulance", "both"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid assignment type. Must be 'doctor', 'ambulance', or 'both'"
        )
    
    # Validate that required IDs are provided based on assignment type
    if assignment_data.assignment_type in ["doctor", "both"] and not assignment_data.doctor_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Doctor ID is required for doctor assignments"
        )
    
    if assignment_data.assignment_type in ["ambulance", "both"] and not assignment_data.ambulance_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ambulance ID is required for ambulance assignments"
        )

    # Ensure patient_id refers to an existing Patient row; if a credential_id was provided by mistake,
    # resolve it to the corresponding Patient.id.
    provided_patient_id = assignment_data.patient_id
    patient = db.query(Patient).filter(Patient.id == provided_patient_id).first()
    if not patient:
        # Try resolving as credential_id
        patient = db.query(Patient).filter(Patient.credential_id == provided_patient_id).first()
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found. Provide a valid patient_id or a patient credential_id.",
            )
        # Map provided credential_id to actual patient.id
        assignment_data.patient_id = patient.id

    # Validate sos_request_id against socket_logs; if not found, set to None to avoid FK violation
    if assignment_data.sos_request_id is not None:
        sos = db.query(SocketLog).filter(SocketLog.id == assignment_data.sos_request_id).first()
        if not sos:
            assignment_data.sos_request_id = None

    # Create the assignment
    db_assignment = PatientAssignment(**assignment_data.dict())
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    return db_assignment


def get_patient_assignment_by_id(db: Session, assignment_id: int) -> Optional[PatientAssignment]:
    """
    Get patient assignment by ID
    """
    return db.query(PatientAssignment).filter(PatientAssignment.id == assignment_id).first()


def get_patient_assignments(
    db: Session, 
    patient_id: int, 
    status: Optional[str] = None, 
    limit: int = 100, 
    offset: int = 0
) -> List[PatientAssignment]:
    """
    Get all assignments for a specific patient
    """
    query = db.query(PatientAssignment).filter(PatientAssignment.patient_id == patient_id)
    
    if status:
        query = query.filter(PatientAssignment.status == status)
    
    return query.offset(offset).limit(limit).all()


def get_doctor_assignments(
    db: Session, 
    doctor_id: int, 
    status: Optional[str] = None, 
    limit: int = 100, 
    offset: int = 0
) -> List[PatientAssignment]:
    """
    Get all assignments for a specific doctor
    """
    query = db.query(PatientAssignment).filter(PatientAssignment.doctor_id == doctor_id)
    
    if status:
        query = query.filter(PatientAssignment.status == status)
    
    return query.offset(offset).limit(limit).all()


def get_ambulance_assignments(
    db: Session, 
    ambulance_id: int, 
    status: Optional[str] = None, 
    limit: int = 100, 
    offset: int = 0
) -> List[PatientAssignment]:
    """
    Get all assignments for a specific ambulance
    """
    query = db.query(PatientAssignment).filter(PatientAssignment.ambulance_id == ambulance_id)
    
    if status:
        query = query.filter(PatientAssignment.status == status)
    
    return query.offset(offset).limit(limit).all()


def get_hospital_assignments(
    db: Session, 
    hospital_id: int, 
    status: Optional[str] = None, 
    limit: int = 100, 
    offset: int = 0
) -> List[PatientAssignment]:
    """
    Get all assignments for a specific hospital
    """
    query = db.query(PatientAssignment).filter(PatientAssignment.hospital_id == hospital_id)
    
    if status:
        query = query.filter(PatientAssignment.status == status)
    
    return query.offset(offset).limit(limit).all()


def get_active_assignments(
    db: Session, 
    hospital_id: Optional[int] = None, 
    limit: int = 100, 
    offset: int = 0
) -> List[PatientAssignment]:
    """
    Get all active assignments
    """
    query = db.query(PatientAssignment).filter(PatientAssignment.status == "active")
    
    if hospital_id:
        query = query.filter(PatientAssignment.hospital_id == hospital_id)
    
    return query.offset(offset).limit(limit).all()


def update_assignment_status(
    db: Session, 
    assignment_id: int, 
    status_update: PatientAssignmentUpdate
) -> PatientAssignment:
    """
    Update assignment status and notes
    """
    assignment = get_patient_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Update only provided fields
    update_data = status_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(assignment, field, value)
    
    assignment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(assignment)
    return assignment


def complete_assignment(
    db: Session, 
    assignment_id: int, 
    completion_notes: str, 
    user_role: str
) -> PatientAssignment:
    """
    Mark assignment as completed
    """
    assignment = get_patient_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Update status based on user role
    if user_role == "doctor":
        assignment.doctor_assignment_status = "completed"
        assignment.doctor_notes = completion_notes
    elif user_role == "ambulance":
        assignment.ambulance_assignment_status = "completed"
        assignment.ambulance_notes = completion_notes
    
    # Check if both doctor and ambulance are completed
    if (assignment.doctor_assignment_status == "completed" and 
        assignment.ambulance_assignment_status == "completed"):
        assignment.status = "completed"
        assignment.case_status = "completed"
        assignment.completed_at = datetime.utcnow()
    
    assignment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(assignment)
    return assignment


def get_assignment_with_context(db: Session, assignment_id: int) -> Dict[str, Any]:
    """
    Get assignment with additional context information
    """
    assignment = get_patient_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Get patient information
    patient = db.query(Patient).filter(Patient.id == assignment.patient_id).first()
    
    # Get doctor information
    doctor = None
    if assignment.doctor_id:
        doctor = db.query(Doctor).filter(Doctor.id == assignment.doctor_id).first()
    
    # Get ambulance information
    ambulance = None
    if assignment.ambulance_id:
        ambulance = db.query(Ambulance).filter(Ambulance.id == assignment.ambulance_id).first()
    
    # Get hospital information
    hospital = db.query(Hospital).filter(Hospital.id == assignment.hospital_id).first()
    
    # Get medical record
    medical_record = db.query(MedicalRecord).filter(MedicalRecord.patient_id == assignment.patient_id).first()
    
    # Build context
    context = {
        "assignment": assignment,
        "patient": {
            "name": patient.full_name if patient else None,
            "email": patient.email if patient else None,
            "phone": patient.phone_number if patient else None,
        } if patient else None,
        "doctor": {
            "name": doctor.name if doctor else None,
            "phone": doctor.phone_number if doctor else None,
            "email": doctor.email if doctor else None,
        } if doctor else None,
        "ambulance": {
            "ambulance_number": ambulance.ambulance_number if ambulance else None,
            "driver_name": ambulance.driver_name if ambulance else None,
            "driver_phone": ambulance.driver_phone if ambulance else None,
        } if ambulance else None,
        "hospital": {
            "name": hospital.name if hospital else None,
            "address": hospital.address if hospital else None,
        } if hospital else None,
        "medical_record": {
            "blood_group": medical_record.blood_group if medical_record else None,
            "allergies": medical_record.allergies if medical_record else None,
            "chronic_conditions": medical_record.chronic_conditions if medical_record else None,
        } if medical_record else None,
    }
    
    return context


def get_assignment_statistics(
    db: Session, 
    hospital_id: Optional[int] = None, 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Get assignment statistics
    """
    query = db.query(PatientAssignment)
    
    if hospital_id:
        query = query.filter(PatientAssignment.hospital_id == hospital_id)
    
    if start_date:
        query = query.filter(PatientAssignment.created_at >= start_date)
    
    if end_date:
        query = query.filter(PatientAssignment.created_at <= end_date)
    
    assignments = query.all()
    
    # Calculate statistics
    total = len(assignments)
    active = len([a for a in assignments if a.status == "active"])
    completed = len([a for a in assignments if a.status == "completed"])
    pending = len([a for a in assignments if a.status == "pending"])
    
    doctor_assignments = len([a for a in assignments if a.assignment_type == "doctor"])
    ambulance_assignments = len([a for a in assignments if a.assignment_type == "ambulance"])
    both_assignments = len([a for a in assignments if a.assignment_type == "both"])
    
    # Status breakdown
    status_counts = {}
    priority_counts = {}
    
    for assignment in assignments:
        status_counts[assignment.status] = status_counts.get(assignment.status, 0) + 1
        priority_counts[assignment.priority_level] = priority_counts.get(assignment.priority_level, 0) + 1
    
    return {
        "total_assignments": total,
        "active_assignments": active,
        "completed_assignments": completed,
        "pending_assignments": pending,
        "doctor_assignments": doctor_assignments,
        "ambulance_assignments": ambulance_assignments,
        "both_assignments": both_assignments,
        "assignments_by_status": status_counts,
        "assignments_by_priority": priority_counts,
    }
