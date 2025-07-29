from fastapi import Depends, HTTPException, status
from app.middleware.auth import get_current_user
from app.db.models.user_model import User

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action"
        )
    return current_user
