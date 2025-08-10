# app/schemas/socket_log.py
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class SocketLogBase(BaseModel):
    event_type: str
    socket_id: str
    user_id: Optional[str] = None
    user_role: Optional[str] = None
    event_data: Optional[Dict[str, Any]] = None
    request_data: Optional[Dict[str, Any]] = None
    response_data: Optional[Dict[str, Any]] = None
    patient_latitude: Optional[str] = None
    patient_longitude: Optional[str] = None
    hospital_id: Optional[int] = None
    hospital_name: Optional[str] = None
    distance_km: Optional[str] = None
    status: str = "pending"
    error_message: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # SOS specific fields
    sos_status: Optional[str] = None
    sos_acceptance_date: Optional[datetime] = None
    sos_rejection_date: Optional[datetime] = None
    sos_expiry_date: Optional[datetime] = None
    accepted_by_hospital_id: Optional[int] = None
    accepted_by_hospital_name: Optional[str] = None
    rejection_reason: Optional[str] = None


class SocketLogCreate(SocketLogBase):
    pass


class SocketLogUpdate(BaseModel):
    status: Optional[str] = None
    response_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    response_time_ms: Optional[int] = None
    
    # SOS specific update fields
    sos_status: Optional[str] = None
    sos_acceptance_date: Optional[datetime] = None
    sos_rejection_date: Optional[datetime] = None
    sos_expiry_date: Optional[datetime] = None
    accepted_by_hospital_id: Optional[int] = None
    accepted_by_hospital_name: Optional[str] = None
    rejection_reason: Optional[str] = None


class SocketLogOut(SocketLogBase):
    id: int
    processed: bool
    created_at: datetime
    processed_at: Optional[datetime] = None
    response_time_ms: Optional[int] = None
    session_duration: Optional[int] = None

    class Config:
        from_attributes = True


class SocketLogStatistics(BaseModel):
    total_events: int
    events_by_type: Dict[str, int]
    events_by_status: Dict[str, int]
    events_by_role: Dict[str, int]
    ambulance_requests: int
    ambulance_responses: int
    response_rate: float
    time_range: Dict[str, str]


class SocketLogFilter(BaseModel):
    event_type: Optional[str] = None
    user_id: Optional[str] = None
    user_role: Optional[str] = None
    hospital_id: Optional[int] = None
    status: Optional[str] = None
    sos_status: Optional[str] = None
    accepted_by_hospital_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
    offset: int = 0


class SOSAcceptanceRequest(BaseModel):
    """Schema for accepting an SOS request"""
    socket_log_id: int
    hospital_id: int
    hospital_name: str
    acceptance_note: Optional[str] = None


class SOSRejectionRequest(BaseModel):
    """Schema for rejecting an SOS request"""
    socket_log_id: int
    hospital_id: int
    hospital_name: str
    rejection_reason: str


class SOSStatusUpdate(BaseModel):
    """Schema for updating SOS status"""
    sos_status: str  # 'accepted', 'rejected', 'expired'
    accepted_by_hospital_id: Optional[int] = None
    accepted_by_hospital_name: Optional[str] = None
    rejection_reason: Optional[str] = None
    sos_acceptance_date: Optional[datetime] = None
    sos_rejection_date: Optional[datetime] = None
    sos_expiry_date: Optional[datetime] = None 