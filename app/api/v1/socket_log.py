# app/api/v1/socket_log.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.session import get_db
from app.utils.deps import get_current_user, require_admin
from app.db.models.credential import Credential
from app.schemas.socket_log import SocketLogOut, SocketLogStatistics, SocketLogFilter
from app.services.socket_log import (
    get_socket_logs_by_user,
    get_socket_logs_by_event_type,
    get_ambulance_requests,
    get_hospital_responses,
    get_socket_logs_by_time_range,
    get_socket_statistics
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