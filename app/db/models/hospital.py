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

    user = relationship("Credential", back_populates="hospital")
    doctors = relationship("Doctor", back_populates="hospital")
    ambulances = relationship("Ambulance", back_populates="hospital")
    socket_logs = relationship("SocketLog", back_populates="hospital")

