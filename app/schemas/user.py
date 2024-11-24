import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.user import Role


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    gender: int
    avatar_id: Optional[uuid.UUID] = None
    bio: Optional[str] = None
    role: Role
    created_at: datetime.datetime
    updated_at: datetime.datetime


class UserCreate(BaseModel):
    username: str
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str


class UserUpdate(BaseModel):
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    gender: Optional[int] = None
    bio: Optional[str] = None
    password: Optional[str] = None

