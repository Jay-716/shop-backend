from typing import Optional

from pydantic import BaseModel, ConfigDict


class StoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    name: str
    description: str
    image_id: Optional[str] = None


class StoreCreate(BaseModel):
    name: str
    description: str
    image_id: Optional[str] = None


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_id: Optional[str] = None
