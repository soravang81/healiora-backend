# app/db/models/credential.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class Credential(Base):
    __tablename__ = "credentials"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=True)
    role = Column(String, default="patient", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # One-to-one relationships to actual entities (optional)
    patient = relationship("Patient", back_populates="credential", uselist=False)
    hospital = relationship("Hospital", back_populates="credential", uselist=False)
    # doctor = relationship("Doctor", back_populates="credential", uselist=False)