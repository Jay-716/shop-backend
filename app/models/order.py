import datetime
from typing import List, Optional

import sqlalchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .user import User, Address
from .good import Good, GoodStyle
from .pay import Payment


class CartItem(Base):
    __tablename__ = "cart"
    id: Mapped[int] = mapped_column(sqlalchemy.types.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship(back_populates="cart_items")
    good_id: Mapped[int] = mapped_column(ForeignKey("good.id"))
    good: Mapped[Good] = relationship(back_populates="cart_items")
    style_id: Mapped[int] = mapped_column(ForeignKey("good_style.id"), nullable=True)
    style: Mapped[GoodStyle] = relationship(back_populates="cart_items")
    count: Mapped[int] = mapped_column(sqlalchemy.types.Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now,
                                                          onupdate=datetime.datetime.now)


class Order(Base):
    __tablename__ = "order"
    id: Mapped[int] = mapped_column(sqlalchemy.types.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship(back_populates="orders")
    total_price: Mapped[int] = mapped_column(sqlalchemy.types.Integer, nullable=True)
    status: Mapped[int] = mapped_column(sqlalchemy.types.SmallInteger, nullable=False, default=0)
    address_id: Mapped[int] = mapped_column(ForeignKey("address.id"))
    address: Mapped[Address] = relationship(back_populates="orders")
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="order")
    payment: Mapped[Payment] = relationship(back_populates="order")
    # goods: Mapped[List[Good]] = relationship(back_populates="orders", secondary="order_item")
    created_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now,
                                                          onupdate=datetime.datetime.now)


class OrderItem(Base):
    __tablename__ = "order_item"
    id: Mapped[int] = mapped_column(sqlalchemy.types.Integer, primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    order: Mapped[Order] = relationship(back_populates="order_items")
    good_id: Mapped[int] = mapped_column(ForeignKey("good.id"))
    good: Mapped[Good] = relationship(back_populates="order_items")
    style_id: Mapped[int] = mapped_column(ForeignKey("good_style.id"), nullable=True)
    style: Mapped[Optional[GoodStyle]] = relationship(back_populates="order_items")
    count: Mapped[int] = mapped_column(sqlalchemy.types.Integer, nullable=False)
    price: Mapped[int] = mapped_column(sqlalchemy.types.Integer, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now,
                                                          onupdate=datetime.datetime.now)
