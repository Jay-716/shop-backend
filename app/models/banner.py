import datetime
import uuid

import sqlalchemy
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Banner(Base):
    __tablename__ = "banner"
    id: Mapped[int] = mapped_column(sqlalchemy.types.Integer, primary_key=True, autoincrement=True)
    image_id: Mapped[str] = mapped_column(sqlalchemy.types.String(256), nullable=False)
    deleted: Mapped[bool] = mapped_column(sqlalchemy.types.SmallInteger, nullable=False, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now,
                                                          onupdate=datetime.datetime.now)
