# app/schemas/user_settings.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserSettingsBase(BaseModel):
    # Profile settings
    full_name: Optional[str] = None
    phone: Optional[str] = None
    timezone: str = "Asia/Kolkata"
    language: str = "en"
    
    # Notification settings
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False
    notification_frequency: str = "realtime"
    
    # Privacy settings
    show_online_status: bool = True
    share_analytics: bool = True
    
    # Appearance settings
    theme: str = "system"
    accent_color: str = "teal"

class UserSettingsCreate(UserSettingsBase):
    pass

class UserSettingsUpdate(BaseModel):
    # Profile settings
    full_name: Optional[str] = None
    phone: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    
    # Notification settings
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    notification_frequency: Optional[str] = None
    
    # Privacy settings
    show_online_status: Optional[bool] = None
    share_analytics: Optional[bool] = None
    
    # Appearance settings
    theme: Optional[str] = None
    accent_color: Optional[str] = None

class UserSettingsResponse(UserSettingsBase):
    id: int
    credential_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserSettingsWithEmail(UserSettingsResponse):
    email: str
    
    class Config:
        from_attributes = True
