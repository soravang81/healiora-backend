# app/db/models/patient_assignment.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class PatientAssignment(Base):
    __tablename__ = "patient_assignments"

    id = Column(Integer, primary_key=True, index=True)
    sos_request_id = Column(BigInteger, ForeignKey("socket_logs.id"), nullable=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=True, index=True)
    ambulance_id = Column(Integer, ForeignKey("ambulances.id"), nullable=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False, index=True)
    
    assignment_type = Column(String(20), nullable=False)  # 'doctor', 'ambulance', 'both'
    assignment_date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    status = Column(String(50), default='active', index=True)  # active, completed, cancelled, transferred
    priority_level = Column(String(20), default='medium')  # low, medium, high, critical
    
    # Medical Context
    emergency_reason = Column(Text, nullable=True)
    symptoms = Column(Text, nullable=True)
    patient_condition = Column(Text, nullable=True)
    
    # Assignment Details
    assignment_notes = Column(Text, nullable=True)
    doctor_notes = Column(Text, nullable=True)
    ambulance_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    # Status Tracking
    doctor_assignment_status = Column(String(50), default='pending', index=True)  # pending, accepted, rejected, completed
    ambulance_assignment_status = Column(String(50), default='pending', index=True)  # pending, accepted, en_route, arrived, completed
    case_status = Column(String(50), default='open', index=True)  # open, in_progress, completed, cancelled
    
    # Relationships
    patient = relationship("Patient", back_populates="assignments")
    doctor = relationship("Doctor", back_populates="assignments")
    ambulance = relationship("Ambulance", back_populates="assignments")
    hospital = relationship("Hospital", back_populates="assignments")
    sos_request = relationship("SocketLog", back_populates="assignments")

    # Computed patient fields (no DB schema change needed)
    @property
    def patient_name(self) -> str:
        return self.patient.full_name if self.patient else None

    @property
    def patient_age(self) -> int:
        return self.patient.age if self.patient else None

    @property
    def patient_gender(self) -> str:
        return self.patient.gender if self.patient else None
    
    def __repr__(self):
        return f"<PatientAssignment(id={self.id}, patient_id={self.patient_id}, doctor_id={self.doctor_id}, ambulance_id={self.ambulance_id}, status='{self.status}')>"
