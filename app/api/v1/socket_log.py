# app/api/v1/socket_log.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.session import get_db
from app.utils.deps import get_current_user, require_admin
from app.db.models.credential import Credential
from app.schemas.socket_log import (
    SocketLogOut, 
    SocketLogStatistics, 
    SocketLogFilter,
    # SOS specific schemas
    SOSAcceptanceRequest,
    SOSRejectionRequest,
    SOSStatusUpdate
)
from app.services.socket_log import (
    get_socket_logs_by_user,
    get_socket_logs_by_event_type,
    get_ambulance_requests,
    get_hospital_responses,
    get_socket_logs_by_time_range,
    get_socket_statistics,
    # SOS specific functions
    accept_sos_request,
    reject_sos_request,
    expire_sos_request,
    get_sos_requests_by_status,
    get_sos_statistics,
    get_sos_requests_by_hospital,
    get_pending_sos_requests
)

router = APIRouter()


@router.get("/my-logs", response_model=List[SocketLogOut])
def get_my_socket_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    event_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Get socket logs for the current user
    """
    logs = get_socket_logs_by_user(db, str(current_user.id), limit, offset)
    
    if event_type:
        logs = [log for log in logs if log.event_type == event_type]
    
    return logs


@router.get("/ambulance-requests", response_model=List[SocketLogOut])
def get_ambulance_request_logs(
    hospital_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(require_admin)
):
    """
    Get ambulance request logs (Admin only)
    """
    return get_ambulance_requests(
        db, hospital_id, status, start_date, end_date, limit, offset
    )


# ============================================================================
# SOS (Save Our Souls) Endpoints
# ============================================================================

@router.post("/sos/accept", response_model=SocketLogOut)
def accept_sos_request_api(
    request: SOSAcceptanceRequest,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Accept an SOS request (Hospital users only)
    """
    if current_user.role != "hospital":
        raise HTTPException(status_code=403, detail="Access denied. Hospital users only.")
    
    # Verify the hospital ID matches the current user's hospital
    # You might need to adjust this based on your user-hospital relationship
    user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
    
    if not user_hospital_id or user_hospital_id != request.hospital_id:
        raise HTTPException(status_code=403, detail="Access denied. Can only accept SOS for your own hospital.")
    
    result = accept_sos_request(
        db=db,
        socket_log_id=request.socket_log_id,
        hospital_id=request.hospital_id,
        hospital_name=request.hospital_name,
        acceptance_note=request.acceptance_note
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="SOS request not found")
    
    return result


@router.post("/sos/reject", response_model=SocketLogOut)
def reject_sos_request_api(
    request: SOSRejectionRequest,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Reject an SOS request (Hospital users only)
    """
    if current_user.role != "hospital":
        raise HTTPException(status_code=403, detail="Access denied. Hospital users only.")
    
    # Verify the hospital ID matches the current user's hospital
    user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
    
    if not user_hospital_id or user_hospital_id != request.hospital_id:
        raise HTTPException(status_code=403, detail="Access denied. Can only reject SOS for your own hospital.")
    
    result = reject_sos_request(
        db=db,
        socket_log_id=request.socket_log_id,
        hospital_id=request.hospital_id,
        hospital_name=request.hospital_name,
        rejection_reason=request.rejection_reason
    )
    
    if not result:
        raise HTTPException(status_code=404, detail="SOS request not found")
    
    return result


@router.post("/sos/expire/{socket_log_id}", response_model=SocketLogOut)
def expire_sos_request_api(
    socket_log_id: int,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(require_admin)
):
    """
    Mark an SOS request as expired (Admin only)
    """
    result = expire_sos_request(db=db, socket_log_id=socket_log_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="SOS request not found")
    
    return result


@router.get("/sos/by-status/{sos_status}", response_model=List[SocketLogOut])
def get_sos_requests_by_status_api(
    sos_status: str,
    hospital_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(require_admin)
):
    """
    Get SOS requests filtered by status (Admin only)
    """
    valid_statuses = ["pending", "accepted", "rejected", "expired"]
    if sos_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid SOS status. Must be one of: {valid_statuses}")
    
    return get_sos_requests_by_status(
        db, sos_status, hospital_id, start_date, end_date, limit, offset
    )


@router.get("/sos/statistics")
def get_sos_statistics_api(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(require_admin)
):
    """
    Get SOS-specific statistics (Admin only)
    """
    return get_sos_statistics(db, start_date, end_date)


@router.get("/sos/by-hospital/{hospital_id}", response_model=List[SocketLogOut])
def get_sos_requests_by_hospital_api(
    hospital_id: int,
    sos_status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(require_admin)
):
    """
    Get SOS requests for a specific hospital (Admin only)
    """
    return get_sos_requests_by_hospital(
        db, hospital_id, sos_status, start_date, end_date, limit, offset
    )


@router.get("/sos/pending", response_model=List[SocketLogOut])
def get_pending_sos_requests_api(
    hospital_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(require_admin)
):
    """
    Get pending SOS requests that need attention (Admin only)
    """
    return get_pending_sos_requests(db, hospital_id, limit)


@router.get("/sos/my-hospital", response_model=List[SocketLogOut])
def get_my_hospital_sos_requests(
    sos_status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Get SOS requests for the current user's hospital (Hospital users only)
    """
    if current_user.role != "hospital":
        raise HTTPException(status_code=403, detail="Access denied. Hospital users only.")
    
    # Get hospital ID from current user
    user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
    
    if not user_hospital_id:
        raise HTTPException(status_code=404, detail="Hospital not found for current user")
    
    return get_sos_requests_by_hospital(
        db, user_hospital_id, sos_status, start_date, end_date, limit, offset
    )


@router.get("/sos/my-hospital/pending", response_model=List[SocketLogOut])
def get_my_hospital_pending_sos_requests(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Get pending SOS requests for the current user's hospital (Hospital users only)
    """
    if current_user.role != "hospital":
        raise HTTPException(status_code=403, detail="Access denied. Hospital users only.")
    
    # Get hospital ID from current user
    user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
    
    if not user_hospital_id:
        raise HTTPException(status_code=404, detail="Hospital not found for current user")
    
    return get_pending_sos_requests(db, user_hospital_id, limit)


@router.get("/sos/dashboard")
def get_sos_dashboard_data(
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Get SOS dashboard data for the current user
    """
    if current_user.role not in ["admin", "hospital"]:
        raise HTTPException(status_code=403, detail="Access denied. Admin or Hospital users only.")
    
    # Get time range for last 30 days
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)
    
    if current_user.role == "admin":
        # Admin gets global statistics
        sos_stats = get_sos_statistics(db, start_date, end_date)
        pending_requests = get_pending_sos_requests(db, limit=10)
        
        return {
            "user_role": "admin",
            "statistics": sos_stats,
            "pending_requests": pending_requests,
            "time_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }
    else:
        # Hospital users get their hospital-specific data
        user_hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
        
        if not user_hospital_id:
            raise HTTPException(status_code=404, detail="Hospital not found for current user")
        
        # Get hospital-specific SOS requests
        hospital_sos_requests = get_sos_requests_by_hospital(
            db, user_hospital_id, start_date=start_date, end_date=end_date, limit=100
        )
        
        # Count by status
        status_counts = {
            "pending": 0,
            "accepted": 0,
            "rejected": 0,
            "expired": 0
        }
        
        for request in hospital_sos_requests:
            if request.sos_status:
                status_counts[request.sos_status] += 1
        
        # Get pending requests for this hospital
        pending_requests = get_pending_sos_requests(db, user_hospital_id, limit=10)
        
        return {
            "user_role": "hospital",
            "hospital_id": user_hospital_id,
            "hospital_name": current_user.hospital.name if hasattr(current_user, 'hospital') and current_user.hospital else None,
            "status_counts": status_counts,
            "pending_requests": pending_requests,
            "recent_requests": hospital_sos_requests[:10],
            "time_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        }


@router.get("/hospital-responses", response_model=List[SocketLogOut])
def get_hospital_response_logs(
    hospital_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(require_admin)
):
    """
    Get hospital response logs (Admin only)
    """
    return get_hospital_responses(
        db, hospital_id, status, start_date, end_date, limit, offset
    )


@router.get("/by-event-type/{event_type}", response_model=List[SocketLogOut])
def get_logs_by_event_type(
    event_type: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(require_admin)
):
    """
    Get socket logs by event type (Admin only)
    """
    return get_socket_logs_by_event_type(db, event_type, limit, offset)


@router.get("/by-time-range", response_model=List[SocketLogOut])
def get_logs_by_time_range(
    start_date: datetime,
    end_date: datetime,
    event_types: Optional[List[str]] = Query(None),
    user_roles: Optional[List[str]] = Query(None),
    limit: int = Query(1000, ge=1, le=5000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(require_admin)
):
    """
    Get socket logs within a time range (Admin only)
    """
    return get_socket_logs_by_time_range(
        db, start_date, end_date, event_types, user_roles, limit, offset
    )


@router.get("/statistics", response_model=SocketLogStatistics)
def get_socket_statistics_api(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: Credential = Depends(require_admin)
):
    """
    Get socket usage statistics (Admin only)
    """
    return get_socket_statistics(db, start_date, end_date)


@router.get("/recent-activity")
def get_recent_activity(
    hours: int = Query(24, ge=1, le=168),  # Default 24 hours, max 1 week
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Get recent socket activity for the current user
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(hours=hours)
    
    logs = get_socket_logs_by_time_range(
        db, start_date, end_date, user_roles=[current_user.role]
    )
    
    # Filter by current user
    user_logs = [log for log in logs if log.user_id == str(current_user.id)]
    
    # Group by event type
    activity_summary = {}
    for log in user_logs:
        if log.event_type not in activity_summary:
            activity_summary[log.event_type] = {
                "count": 0,
                "success_count": 0,
                "failed_count": 0,
                "last_activity": None
            }
        
        activity_summary[log.event_type]["count"] += 1
        if log.status == "success":
            activity_summary[log.event_type]["success_count"] += 1
        elif log.status == "failed":
            activity_summary[log.event_type]["failed_count"] += 1
        
        if not activity_summary[log.event_type]["last_activity"] or log.created_at > activity_summary[log.event_type]["last_activity"]:
            activity_summary[log.event_type]["last_activity"] = log.created_at
    
    return {
        "time_range": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "hours": hours
        },
        "total_events": len(user_logs),
        "activity_summary": activity_summary,
        "recent_logs": user_logs[:10]  # Last 10 events
    }


@router.get("/ambulance-requests/my-hospital", response_model=List[SocketLogOut])
def get_my_hospital_ambulance_requests(
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Get ambulance requests for the current user's hospital (Hospital users only)
    """
    if current_user.role != "hospital":
        raise HTTPException(status_code=403, detail="Access denied. Hospital users only.")
    
    # Get hospital ID from current user
    # You might need to adjust this based on your user-hospital relationship
    hospital_id = current_user.hospital.id if hasattr(current_user, 'hospital') and current_user.hospital else None
    
    if not hospital_id:
        raise HTTPException(status_code=404, detail="Hospital not found for current user")
    
    return get_ambulance_requests(
        db, hospital_id, status, start_date, end_date, limit, offset
    ) 