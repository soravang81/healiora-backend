from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=True)
    age = Column(Integer, nullable=True)
    role = Column("admin" | "doctor" | "patient" | "hospital" , default="patient")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    medical_record = relationship("MedicalRecord", back_populates="user", uselist=False)
    hospital = relationship("Hospital", back_populates="user", uselist=False)
