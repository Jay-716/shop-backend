import uuid
import datetime
from typing import List

import sqlalchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import  Mapped, mapped_column, relationship

from base import Base


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(sqlalchemy.types.Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(sqlalchemy.types.String(64), nullable=False)
    hashed_password: Mapped[str] = mapped_column(sqlalchemy.types.String(256), nullable=False)
    phone_number: Mapped[str] = mapped_column(sqlalchemy.types.String(64))
    email: Mapped[str] = mapped_column(sqlalchemy.types.String(128))
    gender: Mapped[int] = mapped_column(sqlalchemy.types.SmallInteger, default=0)
    avatar_id: Mapped[str] = mapped_column(sqlalchemy.types.Uuid)
    bio: Mapped[str] = mapped_column(sqlalchemy.types.String(256))
    role: Mapped[int] = mapped_column(sqlalchemy.types.SmallInteger, default=0)
    addresses: Mapped[List["Address"]] = relationship(back_populates="user")
    stores: Mapped[List["Store"]] = relationship(back_populates="user")
    cart_items: Mapped[List["CartItem"]] = relationship(back_populates="user")
    created_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now,
                                                          onupdate=datetime.datetime.now)


class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(sqlalchemy.types.Integer, primary_key=True, autoincrement=True)
    postcode: Mapped[str] = mapped_column(sqlalchemy.types.String(64))
    detail: Mapped[str] = mapped_column(sqlalchemy.types.String(256), nullable=False)
    name: Mapped[str] = mapped_column(sqlalchemy.types.String(64), nullable=False)
    phone_number: Mapped[str] = mapped_column(sqlalchemy.types.String(64), nullable=False)
    comment: Mapped[str] = mapped_column(sqlalchemy.types.String(64))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship(back_populates="addresses")
    orders: Mapped[List["Order"]] = relationship(back_populates="address")
    created_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now,
                                                          onupdate=datetime.datetime.now)
