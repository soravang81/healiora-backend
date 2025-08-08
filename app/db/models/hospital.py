# app/db/models/hospital.py
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    credential_id = Column(Integer, ForeignKey("credentials.id", ondelete="CASCADE"), unique=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    pending = Column(Boolean, default=True)
    admin_name = Column(String, nullable=True)
    approved = Column(Boolean, default=False)
    phone = Column(String, unique=True)
    email = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # New fields
    hospital_type = Column(String, nullable=True)  # "government" or "private"
    emergency_available = Column(Boolean, nullable=True)  # True if emergency services available
    available_24_7 = Column(Boolean, nullable=True)  # True if hospital is open 24/7
    registration_number = Column(String, nullable=True)
    departments = Column(String, nullable=True)  # Comma-separated list of departments

    user = relationship("Credential", back_populates="hospital")
    doctors = relationship("Doctor", back_populates="hospital")
    ambulances = relationship("Ambulance", back_populates="hospital")
    socket_logs = relationship("SocketLog", back_populates="hospital", foreign_keys="[SocketLog.hospital_id]")
    accepted_sos_requests = relationship("SocketLog", foreign_keys="[SocketLog.accepted_by_hospital_id]")

