# app/db/models/doctor.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    credential_id = Column(Integer, ForeignKey("credentials.id", ondelete="CASCADE"), unique=True, nullable=False)
    hospital_id = Column(Integer, ForeignKey("hospitals.id", ondelete="CASCADE"), nullable=False)

    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    address = Column(String, nullable=True)
    education = Column(String, nullable=True)
    specialization = Column(String, nullable=True)
    years_of_experience = Column(Float, nullable=True)

    credential = relationship("Credential", back_populates="doctor")
    hospital = relationship("Hospital", back_populates="doctors")
    assignments = relationship("PatientAssignment", back_populates="doctor")