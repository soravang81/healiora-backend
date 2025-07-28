from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    pending = Column(Boolean, default=True)
    approved = Column(Boolean, default=False)
    phone = Column(String, unique=True)
    email = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="hospital")
