import uuid
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class GoodRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    store_id: int
    name: str
    description: str
    price: int
    image_id: Optional[uuid.UUID] = None


class GoodCreate(BaseModel):
    store_id: int
    name: str
    description: str
    price: int
    image_id: Optional[uuid.UUID] = None


class GoodUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    image_id: Optional[uuid.UUID] = None


class GoodDetailRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    good_id: int
    text: Optional[str] = None
    image_id: Optional[uuid.UUID] = None


class GoodDetailFullCreate(BaseModel):
    text: Optional[str] = None
    image_id: Optional[uuid.UUID] = None


class GoodStyleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    good_id: int
    name: str
    description: Optional[str] = None
    price: int
    image_id: Optional[uuid.UUID] = None


class GoodStyleFullCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: int
    image_id: Optional[uuid.UUID] = None


class GoodFullRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    store_id: int
    name: str
    description: str
    price: int
    image_id: Optional[uuid.UUID] = None
    details: List[GoodDetailRead] = None
    styles: List[GoodStyleRead] = None


class GoodFullCreate(BaseModel):
    store_id: int
    name: str
    description: str
    price: int
    image_id: Optional[uuid.UUID] = None
    details: List[GoodDetailFullCreate]
    styles: List[GoodStyleFullCreate]


class GoodFullUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None
    image_id: Optional[uuid.UUID] = None
    details: Optional[List[GoodDetailFullCreate]] = []
    styles: Optional[List[GoodStyleFullCreate]] = []