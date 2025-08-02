# Socket Log System Documentation

## Overview

The Socket Log System is designed to track and monitor all important socket events in the ambulance request system. It provides comprehensive logging, analytics, and audit capabilities for real-time communication between patients and hospitals.

## Features

- **Event Tracking**: Log all socket events (connect, disconnect, ambulance requests, hospital responses)
- **Performance Monitoring**: Track response times and processing status
- **Error Handling**: Capture and log errors with detailed messages
- **Analytics**: Generate statistics and reports
- **Audit Trail**: Maintain complete history of all socket interactions
- **Location Tracking**: Store patient and hospital location data
- **User Activity**: Monitor user behavior and patterns

## Database Schema

### SocketLog Model

```python
class SocketLog(Base):
    __tablename__ = "socket_logs"

    # Event identification
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    socket_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    user_role = Column(String, nullable=True, index=True)
    
    # Event data
    event_data = Column(JSON, nullable=True)
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    
    # Location data
    patient_latitude = Column(String, nullable=True)
    patient_longitude = Column(String, nullable=True)
    hospital_id = Column(Integer, nullable=True, index=True)
    hospital_name = Column(String, nullable=True)
    distance_km = Column(String, nullable=True)
    
    # Status and outcome
    status = Column(String, nullable=False, default='pending')
    error_message = Column(Text, nullable=True)
    processed = Column(Boolean, default=False)
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # Additional metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    session_duration = Column(Integer, nullable=True)
```

## Event Types

| Event Type | Description | Data Captured |
|------------|-------------|---------------|
| `connect` | User connects to socket | User ID, role, connection timestamp |
| `disconnect` | User disconnects from socket | User ID, role, session duration |
| `update_location` | Patient updates location | Patient ID, coordinates, timestamp |
| `ambulance_request` | Patient requests ambulance | Patient details, location, emergency info |
| `hospital_response` | Hospital responds to request | Response type, details, timing |
| `ambulance_accepted` | Ambulance request accepted | Acceptance details, timing |
| `ambulance_rejected` | Ambulance request rejected | Rejection reason, timing |

## API Endpoints

### 1. Get My Socket Logs
```http
GET /api/v1/socket-logs/my-logs
Authorization: Bearer <token>
```

**Query Parameters:**
- `limit` (int): Number of logs to return (default: 100, max: 1000)
- `offset` (int): Number of logs to skip (default: 0)
- `event_type` (string): Filter by event type

**Response:**
```json
[
  {
    "id": 1,
    "event_type": "ambulance_request",
    "socket_id": "abc123",
    "user_id": "patient_123",
    "user_role": "patient",
    "status": "success",
    "created_at": "2025-08-02T18:30:00Z",
    "processed_at": "2025-08-02T18:30:05Z",
    "response_time_ms": 5000
  }
]
```

### 2. Get Ambulance Request Logs (Admin Only)
```http
GET /api/v1/socket-logs/ambulance-requests
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `hospital_id` (int): Filter by hospital
- `status` (string): Filter by status (pending, success, failed)
- `start_date` (datetime): Start date filter
- `end_date` (datetime): End date filter
- `limit` (int): Number of logs to return
- `offset` (int): Number of logs to skip

### 3. Get Hospital Response Logs (Admin Only)
```http
GET /api/v1/socket-logs/hospital-responses
Authorization: Bearer <admin_token>
```

### 4. Get Logs by Event Type (Admin Only)
```http
GET /api/v1/socket-logs/by-event-type/{event_type}
Authorization: Bearer <admin_token>
```

### 5. Get Logs by Time Range (Admin Only)
```http
GET /api/v1/socket-logs/by-time-range
Authorization: Bearer <admin_token>
```

**Query Parameters:**
- `start_date` (datetime): Start date (required)
- `end_date` (datetime): End date (required)
- `event_types` (array): Filter by event types
- `user_roles` (array): Filter by user roles
- `limit` (int): Number of logs to return
- `offset` (int): Number of logs to skip

### 6. Get Socket Statistics (Admin Only)
```http
GET /api/v1/socket-logs/statistics
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "total_events": 1500,
  "events_by_type": {
    "connect": 500,
    "ambulance_request": 200,
    "hospital_response": 180,
    "disconnect": 500
  },
  "events_by_status": {
    "success": 1400,
    "failed": 100
  },
  "events_by_role": {
    "patient": 800,
    "hospital": 700
  },
  "ambulance_requests": 200,
  "ambulance_responses": 180,
  "response_rate": 90.0,
  "time_range": {
    "start_date": "2025-07-02T00:00:00Z",
    "end_date": "2025-08-02T00:00:00Z"
  }
}
```

### 7. Get Recent Activity
```http
GET /api/v1/socket-logs/recent-activity
Authorization: Bearer <token>
```

**Query Parameters:**
- `hours` (int): Hours to look back (default: 24, max: 168)

**Response:**
```json
{
  "time_range": {
    "start_date": "2025-08-01T18:00:00Z",
    "end_date": "2025-08-02T18:00:00Z",
    "hours": 24
  },
  "total_events": 50,
  "activity_summary": {
    "ambulance_request": {
      "count": 5,
      "success_count": 4,
      "failed_count": 1,
      "last_activity": "2025-08-02T17:30:00Z"
    }
  },
  "recent_logs": [...]
}
```

### 8. Get My Hospital Ambulance Requests (Hospital Users Only)
```http
GET /api/v1/socket-logs/ambulance-requests/my-hospital
Authorization: Bearer <hospital_token>
```

## Service Functions

### Core Functions

```python
# Create a new socket log
create_socket_log(
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
    user_agent: Optional[str] = None
) -> SocketLog

# Update an existing socket log
update_socket_log(
    db: Session,
    log_id: int,
    status: Optional[str] = None,
    response_data: Optional[Dict] = None,
    error_message: Optional[str] = None,
    response_time_ms: Optional[int] = None
) -> Optional[SocketLog]

# Get socket logs by user
get_socket_logs_by_user(
    db: Session,
    user_id: str,
    limit: int = 100,
    offset: int = 0
) -> List[SocketLog]

# Get ambulance request logs
get_ambulance_requests(
    db: Session,
    hospital_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[SocketLog]

# Get socket statistics
get_socket_statistics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]

# Clean up old logs
cleanup_old_socket_logs(
    db: Session,
    days_to_keep: int = 90
) -> int
```

## Integration with Socket Service

The socket service automatically logs all important events:

```python
# Example: Logging ambulance request
socket_log = create_socket_log(
    db=db,
    event_type="ambulance_request",
    socket_id=sid,
    user_id=str(patient_id),
    user_role="patient",
    event_data=data,
    request_data=emergency_details,
    patient_latitude=str(patient_lat) if patient_lat else None,
    patient_longitude=str(patient_lon) if patient_lon else None,
    status="pending"
)

# Example: Updating log with success
update_socket_log(
    db, log_id, 
    status="success", 
    response_data=ambulance_alert_data,
    hospital_id=nearest_hospital['id'],
    hospital_name=nearest_hospital['name'],
    distance_km=str(round(nearest_hospital['distance'], 2)),
    response_time_ms=response_time
)
```

## Usage Examples

### 1. Monitor Ambulance Request Performance

```python
# Get ambulance request statistics for the last 30 days
from datetime import datetime, timedelta
from app.services.socket_log import get_socket_statistics

end_date = datetime.utcnow()
start_date = end_date - timedelta(days=30)

stats = get_socket_statistics(db, start_date, end_date)
print(f"Ambulance requests: {stats['ambulance_requests']}")
print(f"Response rate: {stats['response_rate']}%")
```

### 2. Track User Activity

```python
# Get recent activity for a user
from app.services.socket_log import get_socket_logs_by_user

user_logs = get_socket_logs_by_user(db, "patient_123", limit=50)
for log in user_logs:
    print(f"{log.event_type}: {log.status} at {log.created_at}")
```

### 3. Analyze Hospital Performance

```python
# Get ambulance requests for a specific hospital
hospital_requests = get_ambulance_requests(db, hospital_id=1, status="success")
print(f"Successful requests: {len(hospital_requests)}")

# Calculate average response time
response_times = [log.response_time_ms for log in hospital_requests if log.response_time_ms]
avg_response_time = sum(response_times) / len(response_times) if response_times else 0
print(f"Average response time: {avg_response_time}ms")
```

### 4. Error Analysis

```python
# Get failed ambulance requests
failed_requests = get_ambulance_requests(db, status="failed")
for request in failed_requests:
    print(f"Error: {request.error_message}")
    print(f"Patient: {request.user_id}")
    print(f"Time: {request.created_at}")
```

## Monitoring and Alerts

### Key Metrics to Monitor

1. **Response Rate**: Percentage of ambulance requests that receive hospital responses
2. **Response Time**: Average time for hospitals to respond to requests
3. **Error Rate**: Percentage of failed requests
4. **User Activity**: Number of active users and their activity patterns
5. **System Performance**: Socket connection/disconnection rates

### Alert Thresholds

- Response rate < 80%
- Average response time > 30 seconds
- Error rate > 10%
- High number of failed connections

## Data Retention

- **Default retention**: 90 days
- **Configurable**: Can be adjusted based on requirements
- **Automatic cleanup**: Old logs are automatically removed
- **Backup**: Important logs can be exported before cleanup

## Security Considerations

1. **Access Control**: Only authenticated users can access their own logs
2. **Admin Access**: Only admin users can access system-wide statistics
3. **Data Privacy**: Sensitive information is properly handled
4. **Audit Trail**: All access to logs is tracked
5. **Data Encryption**: Logs are stored securely

## Performance Considerations

1. **Indexing**: All frequently queried fields are indexed
2. **Pagination**: Large result sets are paginated
3. **Caching**: Statistics can be cached for better performance
4. **Cleanup**: Regular cleanup prevents database bloat
5. **Monitoring**: Query performance is monitored

## Troubleshooting

### Common Issues

1. **Missing Logs**: Check if the socket service is properly integrated
2. **Performance Issues**: Verify indexes are created and queries are optimized
3. **Permission Errors**: Ensure proper authentication and authorization
4. **Data Inconsistencies**: Check for proper error handling in socket events

### Debug Commands

```python
# Check if logs are being created
logs = get_socket_logs_by_event_type(db, "ambulance_request", limit=10)
print(f"Recent ambulance requests: {len(logs)}")

# Check for errors
error_logs = get_socket_logs_by_time_range(
    db, 
    datetime.utcnow() - timedelta(hours=1), 
    datetime.utcnow(),
    event_types=["ambulance_request"]
)
failed_logs = [log for log in error_logs if log.status == "failed"]
print(f"Failed requests in last hour: {len(failed_logs)}")
```

This socket log system provides comprehensive monitoring and analytics capabilities for the ambulance request system, enabling better performance tracking, debugging, and system optimization. 