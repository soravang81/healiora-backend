# SOS Tracking System

This document describes the enhanced SOS (Save Our Souls) tracking functionality that has been added to the socket_log system.

## Overview

The SOS tracking system allows hospitals to accept or reject emergency ambulance requests, with comprehensive tracking of acceptance/rejection status, timestamps, and reasons.

## New Database Fields

### SOS-Specific Fields Added to `socket_logs` Table

| Field | Type | Description |
|-------|------|-------------|
| `sos_status` | String | Status of SOS request: 'pending', 'accepted', 'rejected', 'expired' |
| `sos_acceptance_date` | DateTime | When the SOS was accepted |
| `sos_rejection_date` | DateTime | When the SOS was rejected |
| `sos_expiry_date` | DateTime | When the SOS expires |
| `accepted_by_hospital_id` | Integer | ID of hospital that accepted/rejected the SOS |
| `accepted_by_hospital_name` | String | Name of hospital that accepted/rejected the SOS |
| `rejection_reason` | Text | Reason for rejection (if applicable) |

## Service Functions

### Core SOS Functions

#### 1. `accept_sos_request()`
```python
def accept_sos_request(
    db: Session,
    socket_log_id: int,
    hospital_id: int,
    hospital_name: str,
    acceptance_note: Optional[str] = None
) -> Optional[SocketLog]
```
- Accepts an SOS request
- Updates `sos_status` to "accepted"
- Sets `sos_acceptance_date` to current timestamp
- Records accepting hospital details
- Updates general status to "success"

#### 2. `reject_sos_request()`
```python
def reject_sos_request(
    db: Session,
    socket_log_id: int,
    hospital_id: int,
    hospital_name: str,
    rejection_reason: str
) -> Optional[SocketLog]
```
- Rejects an SOS request
- Updates `sos_status` to "rejected"
- Sets `sos_rejection_date` to current timestamp
- Records rejecting hospital details and reason
- Updates general status to "failed"

#### 3. `expire_sos_request()`
```python
def expire_sos_request(
    db: Session,
    socket_log_id: int
) -> Optional[SocketLog]
```
- Marks an SOS request as expired
- Updates `sos_status` to "expired"
- Sets `sos_expiry_date` to current timestamp
- Updates general status to "timeout"

### Query Functions

#### 4. `get_sos_requests_by_status()`
```python
def get_sos_requests_by_status(
    db: Session,
    sos_status: str,
    hospital_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[SocketLog]
```
- Get SOS requests filtered by status
- Optional filtering by hospital, date range

#### 5. `get_sos_statistics()`
```python
def get_sos_statistics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]
```
- Get comprehensive SOS statistics
- Returns acceptance/rejection rates
- Counts by status type

#### 6. `get_sos_requests_by_hospital()`
```python
def get_sos_requests_by_hospital(
    db: Session,
    hospital_id: int,
    sos_status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[SocketLog]
```
- Get SOS requests for a specific hospital
- Optional filtering by status and date range

#### 7. `get_pending_sos_requests()`
```python
def get_pending_sos_requests(
    db: Session,
    hospital_id: Optional[int] = None,
    limit: int = 50
) -> List[SocketLog]
```
- Get pending SOS requests that need attention
- Useful for dashboard displays

## Schema Updates

### New Pydantic Models

#### `SOSAcceptanceRequest`
```python
class SOSAcceptanceRequest(BaseModel):
    socket_log_id: int
    hospital_id: int
    hospital_name: str
    acceptance_note: Optional[str] = None
```

#### `SOSRejectionRequest`
```python
class SOSRejectionRequest(BaseModel):
    socket_log_id: int
    hospital_id: int
    hospital_name: str
    rejection_reason: str
```

#### `SOSStatusUpdate`
```python
class SOSStatusUpdate(BaseModel):
    sos_status: str  # 'accepted', 'rejected', 'expired'
    accepted_by_hospital_id: Optional[int] = None
    accepted_by_hospital_name: Optional[str] = None
    rejection_reason: Optional[str] = None
    sos_acceptance_date: Optional[datetime] = None
    sos_rejection_date: Optional[datetime] = None
    sos_expiry_date: Optional[datetime] = None
```

### Updated Models

All existing socket log schemas now include the new SOS fields:
- `SocketLogBase`
- `SocketLogCreate`
- `SocketLogUpdate`
- `SocketLogOut`
- `SocketLogFilter`

## Usage Examples

### Accepting an SOS Request
```python
from app.services.socket_log import accept_sos_request

# Accept an SOS request
result = accept_sos_request(
    db=db,
    socket_log_id=123,
    hospital_id=1,
    hospital_name="City General Hospital",
    acceptance_note="Ambulance dispatched within 5 minutes"
)
```

### Rejecting an SOS Request
```python
from app.services.socket_log import reject_sos_request

# Reject an SOS request
result = reject_sos_request(
    db=db,
    socket_log_id=123,
    hospital_id=1,
    hospital_name="City General Hospital",
    rejection_reason="No available ambulances at this time"
)
```

### Getting SOS Statistics
```python
from app.services.socket_log import get_sos_statistics

# Get SOS statistics for the last 30 days
stats = get_sos_statistics(db)
print(f"Acceptance rate: {stats['acceptance_rate']:.2f}%")
print(f"Rejection rate: {stats['rejection_rate']:.2f}%")
```

### Getting Pending SOS Requests
```python
from app.services.socket_log import get_pending_sos_requests

# Get all pending SOS requests
pending_requests = get_pending_sos_requests(db)
for request in pending_requests:
    print(f"Pending SOS: {request.id} - {request.hospital_name}")
```

## Database Migration

The migration file `7beb32323404_updated_sos.py` adds the new fields to the `socket_logs` table:

```sql
-- New columns added
ALTER TABLE socket_logs ADD COLUMN sos_status VARCHAR;
ALTER TABLE socket_logs ADD COLUMN sos_acceptance_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE socket_logs ADD COLUMN sos_rejection_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE socket_logs ADD COLUMN sos_expiry_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE socket_logs ADD COLUMN accepted_by_hospital_id INTEGER;
ALTER TABLE socket_logs ADD COLUMN accepted_by_hospital_name VARCHAR;
ALTER TABLE socket_logs ADD COLUMN rejection_reason TEXT;

-- Indexes created
CREATE INDEX ix_socket_logs_sos_status ON socket_logs(sos_status);
CREATE INDEX ix_socket_logs_sos_acceptance_date ON socket_logs(sos_acceptance_date);
CREATE INDEX ix_socket_logs_sos_rejection_date ON socket_logs(sos_rejection_date);
CREATE INDEX ix_socket_logs_sos_expiry_date ON socket_logs(sos_expiry_date);
CREATE INDEX ix_socket_logs_accepted_by_hospital_id ON socket_logs(accepted_by_hospital_id);

-- Foreign key constraint
ALTER TABLE socket_logs ADD CONSTRAINT fk_socket_logs_accepted_by_hospital_id 
    FOREIGN KEY (accepted_by_hospital_id) REFERENCES hospitals(id);
```

## SOS Status Flow

1. **Pending** → Initial state when SOS request is created
2. **Accepted** → Hospital accepts the request
3. **Rejected** → Hospital rejects the request
4. **Expired** → Request times out without response

## Integration Points

### Socket.IO Events
- `sos_request` → Creates socket log with `sos_status = "pending"`
- `sos_accept` → Calls `accept_sos_request()`
- `sos_reject` → Calls `reject_sos_request()`
- `sos_expire` → Calls `expire_sos_request()`

### API Endpoints
- `POST /api/v1/socket-logs/sos/accept` → Accept SOS request
- `POST /api/v1/socket-logs/sos/reject` → Reject SOS request
- `GET /api/v1/socket-logs/sos/statistics` → Get SOS statistics
- `GET /api/v1/socket-logs/sos/pending` → Get pending SOS requests

## Benefits

1. **Complete Audit Trail**: Track when SOS requests were accepted/rejected
2. **Performance Metrics**: Calculate acceptance and rejection rates
3. **Hospital Accountability**: Record which hospital handled each request
4. **Reason Tracking**: Understand why requests were rejected
5. **Dashboard Support**: Real-time pending request monitoring
6. **Analytics**: Historical SOS performance analysis

## Future Enhancements

1. **SOS Priority Levels**: High, medium, low priority SOS requests
2. **Auto-Expiry**: Automatic expiration after configurable time
3. **Escalation**: Automatic escalation to other hospitals if rejected
4. **Notifications**: Real-time notifications for pending SOS requests
5. **Performance Alerts**: Alerts for hospitals with low acceptance rates 