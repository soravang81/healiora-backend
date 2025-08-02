# app/db/models/socket_log.py
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class SocketLog(Base):
    __tablename__ = "socket_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # Event identification
    event_type = Column(String, nullable=False, index=True)  # e.g., 'ambulance_request', 'hospital_response', 'connect', 'disconnect'
    socket_id = Column(String, nullable=False, index=True)   # Socket.io session ID
    user_id = Column(String, nullable=True, index=True)      # User ID from JWT token
    user_role = Column(String, nullable=True, index=True)    # 'patient', 'hospital', 'doctor', 'admin'
    
    # Event data
    event_data = Column(JSON, nullable=True)                 # Full event payload
    request_data = Column(JSON, nullable=True)               # Request data (for ambulance requests)
    response_data = Column(JSON, nullable=True)              # Response data (for hospital responses)
    
    # Location data (for ambulance requests)
    patient_latitude = Column(String, nullable=True)
    patient_longitude = Column(String, nullable=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True, index=True)
    hospital_name = Column(String, nullable=True)
    distance_km = Column(String, nullable=True)
    
    # Status and outcome
    status = Column(String, nullable=False, default='pending')  # 'pending', 'success', 'failed', 'timeout'
    error_message = Column(Text, nullable=True)
    processed = Column(Boolean, default=False)                   # Whether the event was processed successfully
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    response_time_ms = Column(Integer, nullable=True)            # Time taken to process the event
    
    # Additional metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(Text, nullable=True)
    session_duration = Column(Integer, nullable=True)            # Session duration in seconds
    
    # Relationships
    hospital = relationship("Hospital", back_populates="socket_logs")
    
    def __repr__(self):
        return f"<SocketLog(id={self.id}, event_type='{self.event_type}', user_id='{self.user_id}', status='{self.status}')>" 