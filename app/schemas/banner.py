import datetime
import uuid

from pydantic import BaseModel


class BannerRead(BaseModel):
    id: int
    image_id: uuid.UUID
    deleted: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class BannerCreate(BaseModel):
    image_id: uuid.UUID


class BannerUpdate(BaseModel):
    image_id: uuid.UUID
