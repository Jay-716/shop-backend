import datetime
from typing import Optional, List, Tuple

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.user import Role


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    phone_number: Optional[str] = None
    email: Optional[str] = None
    gender: int
    avatar_id: Optional[str] = None
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


class AddressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    postcode: Optional[str] = None
    detail: str
    name: str
    phone_number: str
    comment: Optional[str] = None
    user_id: int


class AddressCreate(BaseModel):
    postcode: Optional[str] = None
    detail: str
    name: str
    phone_number: str
    comment: Optional[str] = None


class AddressUpdate(BaseModel):
    postcode: Optional[str] = None
    detail: Optional[str] = None
    name: Optional[str] = None
    phone_number: Optional[str] = None
    comment: Optional[str] = None


class UserProfile(BaseModel):
    reg_days: int
    order_count: int
    good_count: int
    comment_count: int
    timeline: List[Tuple[str, datetime.datetime]]
