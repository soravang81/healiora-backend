# app/api/v1/user_settings.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.middleware.auth import get_current_user
from app.schemas.user_settings import UserSettingsResponse, UserSettingsUpdate, UserSettingsWithEmail
from app.services.user_settings import (
    get_user_settings_with_email,
    update_user_settings,
    get_or_create_user_settings
)
from app.db.models.credential import Credential

router = APIRouter()

@router.get("/me", response_model=UserSettingsWithEmail)
def get_my_settings(
    current_user: Credential = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's settings"""
    settings = get_user_settings_with_email(db, current_user.id)
    if not settings:
        # Create default settings if they don't exist
        default_settings = get_or_create_user_settings(db, current_user.id)
        settings = get_user_settings_with_email(db, current_user.id)
    
    if not settings:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create or retrieve user settings"
        )
    
    return settings

@router.put("/me", response_model=UserSettingsWithEmail)
def update_my_settings(
    settings_update: UserSettingsUpdate,
    current_user: Credential = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's settings"""
    # Ensure settings exist
    get_or_create_user_settings(db, current_user.id)
    
    # Update settings
    updated_settings = update_user_settings(db, current_user.id, settings_update)
    if not updated_settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User settings not found"
        )
    
    # Return updated settings with email
    return get_user_settings_with_email(db, current_user.id)

@router.post("/me/reset", response_model=UserSettingsWithEmail)
def reset_my_settings(
    current_user: Credential = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reset current user's settings to defaults"""
    from app.schemas.user_settings import UserSettingsCreate
    
    # Create default settings (this will replace existing ones)
    default_settings = UserSettingsCreate()
    updated_settings = update_user_settings(db, current_user.id, UserSettingsUpdate(**default_settings.dict()))
    
    if not updated_settings:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset user settings"
        )
    
    return get_user_settings_with_email(db, current_user.id)
