import datetime
from typing import Optional, List, Tuple

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


class StoreProfile(BaseModel):
    day_order_count: int
    month_order_count: int
    day_total_price: int
    month_total_price: int


class StoreGoodProfile(BaseModel):
    day_count: int
    month_count: int
    timeline: List[Tuple[datetime.date, int]]
