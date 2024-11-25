import datetime

from pydantic import BaseModel


class BannerRead(BaseModel):
    id: int
    image_id: str
    deleted: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class BannerCreate(BaseModel):
    image_id: str


class BannerUpdate(BaseModel):
    image_id: str
