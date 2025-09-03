# app/db/models/ambulance.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Ambulance(Base):
    __tablename__ = "ambulances"

    id = Column(Integer, primary_key=True, index=True)
    credential_id = Column(Integer, ForeignKey("credentials.id", ondelete="CASCADE"), unique=True, nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)
    
    ambulance_number = Column(String, unique=True, nullable=False)
    driver_name = Column(String, nullable=False)
    driver_phone = Column(String, nullable=False)
    driver_email = Column(String, nullable=False)
    vehicle_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    credential = relationship("Credential", back_populates="ambulance")
    hospital = relationship("Hospital", back_populates="ambulances")
    assignments = relationship("PatientAssignment", back_populates="ambulance")
