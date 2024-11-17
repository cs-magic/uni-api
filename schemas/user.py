from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = None
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None

class UserResponse(UserBase):
    id: int
    credits: float
    disabled: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    
class CreditsCheck(BaseModel):
    required_credits: float 