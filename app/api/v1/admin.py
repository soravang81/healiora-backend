from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.credential import Credential
from app.schemas.admin import AdminLoginRequest, AdminLoginResponse, AdminInfo
from app.schemas.token import Token
from app.services.admin import admin_login, get_admin_by_id, verify_admin_access
from app.middleware.auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.post("/login", response_model=AdminLoginResponse)
def admin_login_endpoint(
    payload: AdminLoginRequest, 
    db: Session = Depends(get_db)
):
    """
    Admin login endpoint that only allows users with admin role to authenticate.
    
    This endpoint:
    1. Verifies the user exists and password is correct
    2. Checks if the user has admin role
    3. Returns JWT token only for admin users
    
    Args:
        payload: AdminLoginRequest containing email and password
        
    Returns:
        AdminLoginResponse with access token and admin info
        
    Raises:
        401: Invalid credentials
        403: User is not admin
    """
    try:
        token = admin_login(db, payload.email, payload.password)
        return AdminLoginResponse(
            access_token=token.access_token,
            token_type=token.token_type,
            role=token.role,
            user_id=token.user_id,
            message="Admin login successful"
        )
    except HTTPException:
        # Re-raise the HTTPException as is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during admin login"
        )


@router.get("/me", response_model=AdminInfo)
def get_admin_profile(
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Get current admin user profile.
    Only accessible by authenticated admin users.
    
    Args:
        db: Database session
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        AdminInfo with admin user details
        
    Raises:
        403: User is not admin
    """
    # Verify the current user is actually an admin
    if not verify_admin_access(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required."
        )
    
    return AdminInfo(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active
    )


@router.get("/verify", response_model=dict)
def verify_admin_status(
    db: Session = Depends(get_db),
    current_user: Credential = Depends(get_current_user)
):
    """
    Verify if the current user has admin privileges.
    
    Args:
        db: Database session
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        Dictionary with admin verification status
        
    Raises:
        403: User is not admin
    """
    is_admin = verify_admin_access(db, current_user.id)
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required."
        )
    
    return {
        "is_admin": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "message": "Admin access verified"
    } 