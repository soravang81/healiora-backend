# app/schemas/patient_assignment.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class PatientAssignmentCreate(BaseModel):
    sos_request_id: Optional[int] = None  # This will handle both Integer and BigInteger
    patient_id: int
    doctor_id: Optional[int] = None
    ambulance_id: Optional[int] = None
    hospital_id: int
    assignment_type: str  # 'doctor', 'ambulance', 'both'
    priority_level: str = 'medium'  # 'low', 'medium', 'high', 'critical'
    emergency_reason: Optional[str] = None
    symptoms: Optional[str] = None
    patient_condition: Optional[str] = None
    assignment_notes: Optional[str] = None


class PatientAssignmentUpdate(BaseModel):
    status: Optional[str] = None
    priority_level: Optional[str] = None
    emergency_reason: Optional[str] = None
    symptoms: Optional[str] = None
    patient_condition: Optional[str] = None
    assignment_notes: Optional[str] = None
    doctor_notes: Optional[str] = None
    ambulance_notes: Optional[str] = None
    doctor_assignment_status: Optional[str] = None
    ambulance_assignment_status: Optional[str] = None
    case_status: Optional[str] = None
    completed_at: Optional[datetime] = None


class PatientAssignmentOut(BaseModel):
    id: int
    sos_request_id: Optional[int]  # This will handle both Integer and BigInteger
    patient_id: int
    doctor_id: Optional[int]
    ambulance_id: Optional[int]
    hospital_id: int
    assignment_type: str
    assignment_date: datetime
    status: str
    priority_level: str
    emergency_reason: Optional[str]
    symptoms: Optional[str]
    patient_condition: Optional[str]
    assignment_notes: Optional[str]
    doctor_notes: Optional[str]
    ambulance_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    doctor_assignment_status: str
    ambulance_assignment_status: str
    case_status: str
    # Derived patient info
    patient_name: Optional[str] = None
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None

    class Config:
        from_attributes = True


class AssignmentStatusUpdate(BaseModel):
    status: Optional[str] = None
    doctor_assignment_status: Optional[str] = None
    ambulance_assignment_status: Optional[str] = None
    case_status: Optional[str] = None
    doctor_notes: Optional[str] = None
    ambulance_notes: Optional[str] = None
    assignment_notes: Optional[str] = None


class PatientAssignmentWithContext(PatientAssignmentOut):
    patient_name: Optional[str] = None
    patient_email: Optional[str] = None
    patient_phone: Optional[str] = None
    doctor_name: Optional[str] = None
    doctor_phone: Optional[str] = None
    doctor_email: Optional[str] = None
    ambulance_number: Optional[str] = None
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None
    hospital_name: Optional[str] = None
    hospital_address: Optional[str] = None
    medical_record_summary: Optional[Dict[str, Any]] = None


class AssignmentStatistics(BaseModel):
    total_assignments: int
    active_assignments: int
    completed_assignments: int
    pending_assignments: int
    doctor_assignments: int
    ambulance_assignments: int
    both_assignments: int
    assignments_by_status: Dict[str, int]
    assignments_by_priority: Dict[str, int]
