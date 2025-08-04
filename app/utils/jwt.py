from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

# Secret key and algorithm — store securely in env vars in production
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def create_access_token(user_id: int, role: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"user_id": user_id, "role": role}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = int(expire.timestamp())  # UNIX timestamp
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        role = payload.get("role")
        if user_id is None or role is None:
            raise JWTError("user_id or role missing in token")
        return {"user_id": user_id, "role": role}
    except JWTError:
        raise JWTError("Invalid token")
