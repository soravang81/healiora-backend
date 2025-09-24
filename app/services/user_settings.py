# app/services/user_settings.py
from sqlalchemy.orm import Session
from app.db.models.user_settings import UserSettings
from app.db.models.credential import Credential
from app.schemas.user_settings import UserSettingsCreate, UserSettingsUpdate, UserSettingsResponse, UserSettingsWithEmail
from typing import Optional

def get_user_settings_by_credential_id(db: Session, credential_id: int) -> Optional[UserSettings]:
    """Get user settings by credential ID"""
    return db.query(UserSettings).filter(UserSettings.credential_id == credential_id).first()

def create_user_settings(db: Session, credential_id: int, settings: UserSettingsCreate) -> UserSettings:
    """Create new user settings"""
    db_settings = UserSettings(
        credential_id=credential_id,
        **settings.dict()
    )
    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings

def update_user_settings(db: Session, credential_id: int, settings: UserSettingsUpdate) -> Optional[UserSettings]:
    """Update user settings"""
    db_settings = get_user_settings_by_credential_id(db, credential_id)
    if not db_settings:
        return None
    
    update_data = settings.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_settings, field, value)
    
    db.commit()
    db.refresh(db_settings)
    return db_settings

def get_or_create_user_settings(db: Session, credential_id: int) -> UserSettings:
    """Get existing user settings or create default ones"""
    settings = get_user_settings_by_credential_id(db, credential_id)
    if not settings:
        # Create default settings
        default_settings = UserSettingsCreate()
        settings = create_user_settings(db, credential_id, default_settings)
    return settings

def get_user_settings_with_email(db: Session, credential_id: int) -> Optional[UserSettingsWithEmail]:
    """Get user settings with email from credential"""
    settings = get_user_settings_by_credential_id(db, credential_id)
    if not settings:
        return None
    
    credential = db.query(Credential).filter(Credential.id == credential_id).first()
    if not credential:
        return None
    
    # Convert to response format
    settings_dict = {
        "id": settings.id,
        "credential_id": settings.credential_id,
        "full_name": settings.full_name,
        "phone": settings.phone,
        "timezone": settings.timezone,
        "language": settings.language,
        "email_notifications": settings.email_notifications,
        "push_notifications": settings.push_notifications,
        "sms_notifications": settings.sms_notifications,
        "notification_frequency": settings.notification_frequency,
        "show_online_status": settings.show_online_status,
        "share_analytics": settings.share_analytics,
        "theme": settings.theme,
        "accent_color": settings.accent_color,
        "created_at": settings.created_at,
        "updated_at": settings.updated_at,
        "email": credential.email
    }
    
    return UserSettingsWithEmail(**settings_dict)
