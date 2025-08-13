# app/services/socket_log.py
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from app.db.models.socket_log import SocketLog


def create_socket_log(
    db: Session,
    event_type: str,
    socket_id: str,
    user_id: Optional[str] = None,
    user_role: Optional[str] = None,
    event_data: Optional[Dict] = None,
    request_data: Optional[Dict] = None,
    response_data: Optional[Dict] = None,
    patient_latitude: Optional[str] = None,
    patient_longitude: Optional[str] = None,
    hospital_id: Optional[int] = None,
    hospital_name: Optional[str] = None,
    distance_km: Optional[str] = None,
    status: str = "pending",
    error_message: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    # SOS specific fields
    sos_status: Optional[str] = None,
    sos_acceptance_date: Optional[datetime] = None,
    sos_rejection_date: Optional[datetime] = None,
    sos_expiry_date: Optional[datetime] = None,
    accepted_by_hospital_id: Optional[int] = None,
    accepted_by_hospital_name: Optional[str] = None,
    rejection_reason: Optional[str] = None
) -> SocketLog:
    """
    Create a new socket log entry
    """
    socket_log = SocketLog(
        event_type=event_type,
        socket_id=socket_id,
        user_id=user_id,
        user_role=user_role,
        event_data=event_data,
        request_data=request_data,
        response_data=response_data,
        patient_latitude=patient_latitude,
        patient_longitude=patient_longitude,
        hospital_id=hospital_id,
        hospital_name=hospital_name,
        distance_km=distance_km,
        status=status,
        error_message=error_message,
        ip_address=ip_address,
        user_agent=user_agent,
        # SOS specific fields
        sos_status=sos_status,
        sos_acceptance_date=sos_acceptance_date,
        sos_rejection_date=sos_rejection_date,
        sos_expiry_date=sos_expiry_date,
        accepted_by_hospital_id=accepted_by_hospital_id,
        accepted_by_hospital_name=accepted_by_hospital_name,
        rejection_reason=rejection_reason
    )
    
    db.add(socket_log)
    db.commit()
    db.refresh(socket_log)
    return socket_log


def update_socket_log(
    db: Session,
    log_id: int,
    status: Optional[str] = None,
    response_data: Optional[Dict] = None,
    error_message: Optional[str] = None,
    response_time_ms: Optional[int] = None,
    # SOS specific update fields
    sos_status: Optional[str] = None,
    sos_acceptance_date: Optional[datetime] = None,
    sos_rejection_date: Optional[datetime] = None,
    sos_expiry_date: Optional[datetime] = None,
    accepted_by_hospital_id: Optional[int] = None,
    accepted_by_hospital_name: Optional[str] = None,
    rejection_reason: Optional[str] = None
) -> Optional[SocketLog]:
    """
    Update an existing socket log entry
    """
    socket_log = db.query(SocketLog).filter(SocketLog.id == log_id).first()
    if not socket_log:
        return None
    
    if status:
        socket_log.status = status
    if response_data:
        socket_log.response_data = response_data
    if error_message:
        socket_log.error_message = error_message
    if response_time_ms:
        socket_log.response_time_ms = response_time_ms
    
    # Update SOS specific fields
    if sos_status:
        socket_log.sos_status = sos_status
    if sos_acceptance_date:
        socket_log.sos_acceptance_date = sos_acceptance_date
    if sos_rejection_date:
        socket_log.sos_rejection_date = sos_rejection_date
    if sos_expiry_date:
        socket_log.sos_expiry_date = sos_expiry_date
    if accepted_by_hospital_id:
        socket_log.accepted_by_hospital_id = accepted_by_hospital_id
    if accepted_by_hospital_name:
        socket_log.accepted_by_hospital_name = accepted_by_hospital_name
    if rejection_reason:
        socket_log.rejection_reason = rejection_reason
    
    # Mark as processed and set processed_at timestamp
    socket_log.processed = True
    socket_log.processed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(socket_log)
    return socket_log


def get_socket_logs_by_user(
    db: Session,
    user_id: str,
    limit: int = 100,
    offset: int = 0
) -> List[SocketLog]:
    """
    Get socket logs for a specific user
    """
    return db.query(SocketLog).filter(
        SocketLog.user_id == user_id
    ).order_by(desc(SocketLog.created_at)).offset(offset).limit(limit).all()


def get_socket_logs_by_event_type(
    db: Session,
    event_type: str,
    limit: int = 100,
    offset: int = 0
) -> List[SocketLog]:
    """
    Get socket logs by event type
    """
    return db.query(SocketLog).filter(
        SocketLog.event_type == event_type
    ).order_by(desc(SocketLog.created_at)).offset(offset).limit(limit).all()


def get_ambulance_requests(
    db: Session,
    hospital_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[SocketLog]:
    """
    Get ambulance request logs with optional filtering
    """
    query = db.query(SocketLog).filter(SocketLog.event_type == "ambulance_request")
    
    if hospital_id:
        query = query.filter(SocketLog.hospital_id == hospital_id)
    if status:
        query = query.filter(SocketLog.status == status)
    if start_date:
        query = query.filter(SocketLog.created_at >= start_date)
    if end_date:
        query = query.filter(SocketLog.created_at <= end_date)
    
    return query.order_by(desc(SocketLog.created_at)).offset(offset).limit(limit).all()


def get_hospital_responses(
    db: Session,
    hospital_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[SocketLog]:
    """
    Get hospital response logs with optional filtering
    """
    query = db.query(SocketLog).filter(SocketLog.event_type == "hospital_response")
    
    if hospital_id:
        query = query.filter(SocketLog.hospital_id == hospital_id)
    if status:
        query = query.filter(SocketLog.status == status)
    if start_date:
        query = query.filter(SocketLog.created_at >= start_date)
    if end_date:
        query = query.filter(SocketLog.created_at <= end_date)
    
    return query.order_by(desc(SocketLog.created_at)).offset(offset).limit(limit).all()


def get_socket_logs_by_time_range(
    db: Session,
    start_date: datetime,
    end_date: datetime,
    event_types: Optional[List[str]] = None,
    user_roles: Optional[List[str]] = None,
    limit: int = 1000,
    offset: int = 0
) -> List[SocketLog]:
    """
    Get socket logs within a time range with optional filtering
    """
    query = db.query(SocketLog).filter(
        and_(
            SocketLog.created_at >= start_date,
            SocketLog.created_at <= end_date
        )
    )
    
    if event_types:
        query = query.filter(SocketLog.event_type.in_(event_types))
    if user_roles:
        query = query.filter(SocketLog.user_role.in_(user_roles))
    
    return query.order_by(desc(SocketLog.created_at)).offset(offset).limit(limit).all()


def get_socket_statistics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Get socket usage statistics
    """
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Total events
    total_events = db.query(SocketLog).filter(
        and_(
            SocketLog.created_at >= start_date,
            SocketLog.created_at <= end_date
        )
    ).count()
    
    # Events by type
    events_by_type = db.query(
        SocketLog.event_type,
        db.func.count(SocketLog.id).label('count')
    ).filter(
        and_(
            SocketLog.created_at >= start_date,
            SocketLog.created_at <= end_date
        )
    ).group_by(SocketLog.event_type).all()
    
    # Events by status
    events_by_status = db.query(
        SocketLog.status,
        db.func.count(SocketLog.id).label('count')
    ).filter(
        and_(
            SocketLog.created_at >= start_date,
            SocketLog.created_at <= end_date
        )
    ).group_by(SocketLog.status).all()
    
    # Events by user role
    events_by_role = db.query(
        SocketLog.user_role,
        db.func.count(SocketLog.id).label('count')
    ).filter(
        and_(
            SocketLog.created_at >= start_date,
            SocketLog.created_at <= end_date,
            SocketLog.user_role.isnot(None)
        )
    ).group_by(SocketLog.user_role).all()
    
    # Ambulance request statistics
    ambulance_requests = db.query(SocketLog).filter(
        and_(
            SocketLog.event_type == "ambulance_request",
            SocketLog.created_at >= start_date,
            SocketLog.created_at <= end_date
        )
    ).count()
    
    ambulance_responses = db.query(SocketLog).filter(
        and_(
            SocketLog.event_type == "hospital_response",
            SocketLog.created_at >= start_date,
            SocketLog.created_at <= end_date
        )
    ).count()
    
    return {
        "total_events": total_events,
        "events_by_type": dict(events_by_type),
        "events_by_status": dict(events_by_status),
        "events_by_role": dict(events_by_role),
        "ambulance_requests": ambulance_requests,
        "ambulance_responses": ambulance_responses,
        "response_rate": (ambulance_responses / ambulance_requests * 100) if ambulance_requests > 0 else 0,
        "time_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    }


def cleanup_old_socket_logs(
    db: Session,
    days_to_keep: int = 90
) -> int:
    """
    Clean up socket logs older than specified days
    Returns the number of deleted records
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
    
    deleted_count = db.query(SocketLog).filter(
        SocketLog.created_at < cutoff_date
    ).delete()
    
    db.commit()
    return deleted_count


def accept_sos_request(
    db: Session,
    socket_log_id: int,
    hospital_id: int,
    hospital_name: str,
    acceptance_note: Optional[str] = None
) -> Optional[SocketLog]:
    """
    Accept an SOS request by updating the socket log with acceptance details
    """
    socket_log = db.query(SocketLog).filter(SocketLog.id == socket_log_id).first()
    if not socket_log:
        return None
    
    # Update SOS status to accepted
    socket_log.sos_status = "accepted"
    socket_log.sos_acceptance_date = datetime.utcnow()
    socket_log.accepted_by_hospital_id = hospital_id
    socket_log.accepted_by_hospital_name = hospital_name
    
    # Update general status
    socket_log.status = "success"
    socket_log.processed = True
    socket_log.processed_at = datetime.utcnow()
    
    # Add acceptance note to response data if provided
    if acceptance_note:
        if not socket_log.response_data:
            socket_log.response_data = {}
        socket_log.response_data["acceptance_note"] = acceptance_note
    
    db.commit()
    db.refresh(socket_log)
    return socket_log


def reject_sos_request(
    db: Session,
    socket_log_id: int,
    hospital_id: int,
    hospital_name: str,
    rejection_reason: str
) -> Optional[SocketLog]:
    """
    Reject an SOS request by updating the socket log with rejection details
    """
    socket_log = db.query(SocketLog).filter(SocketLog.id == socket_log_id).first()
    if not socket_log:
        return None
    
    # Update SOS status to rejected
    socket_log.sos_status = "rejected"
    socket_log.sos_rejection_date = datetime.utcnow()
    socket_log.accepted_by_hospital_id = hospital_id
    socket_log.accepted_by_hospital_name = hospital_name
    socket_log.rejection_reason = rejection_reason
    
    # Update general status
    socket_log.status = "failed"
    socket_log.processed = True
    socket_log.processed_at = datetime.utcnow()
    
    # Add rejection reason to response data
    if not socket_log.response_data:
        socket_log.response_data = {}
    socket_log.response_data["rejection_reason"] = rejection_reason
    
    db.commit()
    db.refresh(socket_log)
    return socket_log


def expire_sos_request(
    db: Session,
    socket_log_id: int
) -> Optional[SocketLog]:
    """
    Mark an SOS request as expired
    """
    socket_log = db.query(SocketLog).filter(SocketLog.id == socket_log_id).first()
    if not socket_log:
        return None
    
    # Update SOS status to expired
    socket_log.sos_status = "expired"
    socket_log.sos_expiry_date = datetime.utcnow()
    
    # Update general status
    socket_log.status = "timeout"
    socket_log.processed = True
    socket_log.processed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(socket_log)
    return socket_log


def get_sos_requests_by_status(
    db: Session,
    sos_status: str,
    hospital_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[SocketLog]:
    """
    Get SOS requests filtered by status
    """
    query = db.query(SocketLog).filter(
        and_(
            SocketLog.event_type == "ambulance_request",
            SocketLog.sos_status == sos_status
        )
    )
    
    if hospital_id:
        query = query.filter(SocketLog.hospital_id == hospital_id)
    if start_date:
        query = query.filter(SocketLog.created_at >= start_date)
    if end_date:
        query = query.filter(SocketLog.created_at <= end_date)
    
    return query.order_by(desc(SocketLog.created_at)).offset(offset).limit(limit).all()


def get_sos_statistics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Get SOS-specific statistics
    """
    if not start_date:
        start_date = datetime.utcnow() - timedelta(days=30)
    if not end_date:
        end_date = datetime.utcnow()
    
    # Total SOS requests
    total_sos_requests = db.query(SocketLog).filter(
        and_(
            SocketLog.event_type == "ambulance_request",
            SocketLog.created_at >= start_date,
            SocketLog.created_at <= end_date
        )
    ).count()
    
    # SOS requests by status
    sos_by_status = db.query(
        SocketLog.sos_status,
        func.count(SocketLog.id).label('count')
    ).filter(
        and_(
            SocketLog.event_type == "ambulance_request",
            SocketLog.created_at >= start_date,
            SocketLog.created_at <= end_date,
            SocketLog.sos_status.isnot(None)
        )
    ).group_by(SocketLog.sos_status).all()
    
    # Accepted SOS requests
    accepted_sos = db.query(SocketLog).filter(
        and_(
            SocketLog.event_type == "ambulance_request",
            SocketLog.sos_status == "accepted",
            SocketLog.created_at >= start_date,
            SocketLog.created_at <= end_date
        )
    ).count()
    
    # Rejected SOS requests
    rejected_sos = db.query(SocketLog).filter(
        and_(
            SocketLog.event_type == "ambulance_request",
            SocketLog.sos_status == "rejected",
            SocketLog.created_at >= start_date,
            SocketLog.created_at <= end_date
        )
    ).count()
    
    # Expired SOS requests
    expired_sos = db.query(SocketLog).filter(
        and_(
            SocketLog.event_type == "ambulance_request",
            SocketLog.sos_status == "expired",
            SocketLog.created_at >= start_date,
            SocketLog.created_at <= end_date
        )
    ).count()
    
    # Pending SOS requests
    pending_sos = db.query(SocketLog).filter(
        and_(
            SocketLog.event_type == "ambulance_request",
            SocketLog.sos_status == "pending",
            SocketLog.created_at >= start_date,
            SocketLog.created_at <= end_date
        )
    ).count()
    
    return {
        "total_sos_requests": total_sos_requests,
        "sos_by_status": dict(sos_by_status),
        "accepted_sos": accepted_sos,
        "rejected_sos": rejected_sos,
        "expired_sos": expired_sos,
        "pending_sos": pending_sos,
        "acceptance_rate": (accepted_sos / total_sos_requests * 100) if total_sos_requests > 0 else 0,
        "rejection_rate": (rejected_sos / total_sos_requests * 100) if total_sos_requests > 0 else 0,
        "time_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
    }


def get_sos_requests_by_hospital(
    db: Session,
    hospital_id: int,
    sos_status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[SocketLog]:
    """
    Get SOS requests for a specific hospital
    """
    query = db.query(SocketLog).filter(
        and_(
            SocketLog.event_type == "ambulance_request",
            SocketLog.hospital_id == hospital_id
        )
    )
    
    if sos_status:
        query = query.filter(SocketLog.sos_status == sos_status)
    if start_date:
        query = query.filter(SocketLog.created_at >= start_date)
    if end_date:
        query = query.filter(SocketLog.created_at <= end_date)
    
    return query.order_by(desc(SocketLog.created_at)).offset(offset).limit(limit).all()


def get_pending_sos_requests(
    db: Session,
    hospital_id: Optional[int] = None,
    limit: int = 50
) -> List[SocketLog]:
    """
    Get pending SOS requests that need attention
    """
    query = db.query(SocketLog).filter(
        and_(
            SocketLog.event_type == "ambulance_request",
            SocketLog.sos_status == "pending"
        )
    )
    
    if hospital_id:
        query = query.filter(SocketLog.hospital_id == hospital_id)
    
    return query.order_by(SocketLog.created_at).limit(limit).all() 