from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Optional[str] = None
    user_id: Optional[int] = None
