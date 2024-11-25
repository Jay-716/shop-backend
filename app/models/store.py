import datetime
from typing import List

import sqlalchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .user import User


class Store(Base):
    __tablename__ = "store"
    id: Mapped[int] = mapped_column(sqlalchemy.types.Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    owner: Mapped[User] = relationship("User", back_populates="stores")
    name: Mapped[str] = mapped_column(sqlalchemy.types.String(256), nullable=False)
    description: Mapped[str] = mapped_column(sqlalchemy.types.String(512), nullable=False)
    image_id: Mapped[str] = mapped_column(sqlalchemy.types.String(256), nullable=True)
    goods: Mapped[List["Good"]] = relationship(back_populates="store")
    created_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now,
                                                          onupdate=datetime.datetime.now)

