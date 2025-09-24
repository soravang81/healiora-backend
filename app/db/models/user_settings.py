# app/db/models/user_settings.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    credential_id = Column(Integer, ForeignKey("credentials.id"), unique=True, nullable=False)
    
    # Profile settings
    full_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    timezone = Column(String, default="Asia/Kolkata", nullable=False)
    language = Column(String, default="en", nullable=False)
    
    # Notification settings
    email_notifications = Column(Boolean, default=True, nullable=False)
    push_notifications = Column(Boolean, default=True, nullable=False)
    sms_notifications = Column(Boolean, default=False, nullable=False)
    notification_frequency = Column(String, default="realtime", nullable=False)
    
    # Privacy settings
    show_online_status = Column(Boolean, default=True, nullable=False)
    share_analytics = Column(Boolean, default=True, nullable=False)
    
    # Appearance settings
    theme = Column(String, default="system", nullable=False)
    accent_color = Column(String, default="teal", nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    credential = relationship("Credential", back_populates="user_settings")
