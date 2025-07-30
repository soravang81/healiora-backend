from fastapi import Depends, HTTPException, status
from app.middleware.auth import get_current_user
from app.db.models.credential import Credential  # ✅ updated to use Credential

def require_admin(current_user: Credential = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can perform this action"
        )
    return current_user
