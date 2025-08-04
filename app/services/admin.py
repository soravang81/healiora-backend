from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.db.models.credential import Credential
from app.core.security import verify_password
from app.utils.jwt import create_access_token
from app.schemas.token import Token
from typing import Optional


def admin_login(db: Session, email: str, password: str) -> Token:
    """
    Admin login function that verifies credentials and checks admin role.
    Only users with role 'admin' can successfully log in.
    
    Args:
        db: Database session
        email: User's email address
        password: User's plain text password
        
    Returns:
        Token object with access token and user info
        
    Raises:
        HTTPException: If credentials are invalid or user is not admin
    """
    # Get user by email
    user = db.query(Credential).filter(Credential.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    # Check if user has admin role
    if user.role.lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Admin privileges required."
        )
    
    # Create access token
    access_token = create_access_token(user_id=user.id, role=user.role)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role,
        user_id=user.id
    )


def get_admin_by_id(db: Session, admin_id: int) -> Optional[Credential]:
    """
    Get admin user by ID, ensuring they have admin role.
    
    Args:
        db: Database session
        admin_id: Admin user ID
        
    Returns:
        Credential object if admin exists and has admin role, None otherwise
    """
    user = db.query(Credential).filter(
        Credential.id == admin_id,
        Credential.role == "admin",
        Credential.is_active == True
    ).first()
    
    return user


def get_admin_by_email(db: Session, email: str) -> Optional[Credential]:
    """
    Get admin user by email, ensuring they have admin role.
    
    Args:
        db: Database session
        email: Admin user email
        
    Returns:
        Credential object if admin exists and has admin role, None otherwise
    """
    user = db.query(Credential).filter(
        Credential.email == email,
        Credential.role == "admin",
        Credential.is_active == True
    ).first()
    
    return user


def verify_admin_access(db: Session, user_id: int) -> bool:
    """
    Verify if a user has admin access.
    
    Args:
        db: Database session
        user_id: User ID to check
        
    Returns:
        True if user is admin, False otherwise
    """
    user = db.query(Credential).filter(
        Credential.id == user_id,
        Credential.role == "admin",
        Credential.is_active == True
    ).first()
    
    return user is not None
