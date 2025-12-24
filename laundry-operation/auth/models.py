from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime


class UserInDB(BaseModel):
    id: str
    username: str
    email: str
    hashed_password: str
    full_name: Optional[str] = None
    created_at: datetime
