import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .user import AddressRead
from .good import GoodRead, GoodStyleRead


class CartItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    good_id: int
    good: GoodRead
    style_id: Optional[int] = None
    style: Optional[GoodStyleRead] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime


class CartItemCreate(BaseModel):
    good_id: int
    style_id: Optional[int] = None
    count: int


class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    total_price: int
    status: int
    address_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class OrderFullRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    total_price: int
    status: int
    address_id: int
    address: AddressRead
    order_items: List["OrderItemFullRead"]
    created_at: datetime.datetime
    updated_at: datetime.datetime


class OrderFullCreate(BaseModel):
    address_id: int
    goods: List["OrderItemFullCreate"]


class OrderFullUpdate(BaseModel):
    address_id: Optional[int] = None
    goods: Optional[List["OrderItemFullCreate"]] = None


class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_id: int
    good_id: int
    style_id: Optional[int] = None
    count: int
    price: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class OrderItemFullRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_id: int
    good_id: int
    good: GoodRead
    style_id: Optional[int] = None
    style: Optional[GoodStyleRead] = None
    count: int
    price: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class OrderItemFullCreate(BaseModel):
    good_id: int
    style_id: Optional[int] = None
    count: int
