from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

# Secret key and algorithm — store securely in env vars in production
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = {"user_id": user_id}
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode["exp"] = int(expire.timestamp())  # Convert datetime to UNIX timestamp
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {payload}")  # Debugging line
        user_id = payload.get("user_id")
        if user_id is None:
            raise JWTError("user_id missing in token")
        return {"user_id": user_id}
    except JWTError:
        raise JWTError("Invalid token")
    

