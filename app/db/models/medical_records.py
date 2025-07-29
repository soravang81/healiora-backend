from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)


    date_of_birth = Column(Date, nullable=False)
    blood_group = Column(String(3), nullable=True)  # e.g., A+, O-, etc.

    past_surgeries = Column(Text, nullable=True)
    long_term_medications = Column(Text, nullable=True)
    ongoing_illnesses = Column(Text, nullable=True)
    allergies = Column(Text, nullable=True)
    other_issues = Column(Text, nullable=True)

    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_number = Column(String(20), nullable=True)

    # Optional: create relationship to User model
    patient = relationship("Patient", back_populates="medical_record")

