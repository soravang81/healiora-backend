# app/db/models/patient.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    credential_id = Column(Integer, ForeignKey("credentials.id", ondelete="CASCADE"), unique=True)
    username = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    emergency_contact = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    credential = relationship("Credential", back_populates="patient")
    medical_record = relationship("MedicalRecord", back_populates="patient", uselist=False)
