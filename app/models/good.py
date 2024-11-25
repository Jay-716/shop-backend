import datetime
from typing import List

import sqlalchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .store import Store


class Good(Base):
    __tablename__ = "good"
    id: Mapped[int] = mapped_column(sqlalchemy.types.Integer, primary_key=True, autoincrement=True)
    store_id: Mapped[int] = mapped_column(ForeignKey("store.id"))
    store: Mapped[Store] = relationship(back_populates="goods")
    name: Mapped[str] = mapped_column(sqlalchemy.types.String(256), nullable=False)
    description: Mapped[str] = mapped_column(sqlalchemy.types.String(512), nullable=False)
    price: Mapped[int] = mapped_column(sqlalchemy.types.Integer, nullable=False)
    image_id: Mapped[str] = mapped_column(sqlalchemy.types.String(256), nullable=True)
    details: Mapped[List["GoodDetail"]] = relationship(back_populates="good")
    styles: Mapped[List["GoodStyle"]] = relationship(back_populates="good")
    tag_links: Mapped[List["TagGoodLink"]] = relationship(back_populates="good")
    cart_items: Mapped[List["CartItem"]] = relationship(back_populates="good")
    order_items: Mapped["OrderItem"] = relationship(back_populates="good")
    # orders: Mapped[List["Order"]] = relationship(back_populates="goods", secondary="order_item")
    created_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now,
                                                          onupdate=datetime.datetime.now)


class GoodDetail(Base):
    __tablename__ = "good_detail"
    id: Mapped[int] = mapped_column(sqlalchemy.types.Integer, primary_key=True, autoincrement=True)
    good_id: Mapped[int] = mapped_column(ForeignKey("good.id"))
    good: Mapped[Good] = relationship(back_populates="details")
    text: Mapped[str] = mapped_column(sqlalchemy.types.Text, nullable=True)
    image_id: Mapped[str] = mapped_column(sqlalchemy.types.String(256), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now,
                                                          onupdate=datetime.datetime.now)


class GoodStyle(Base):
    __tablename__ = "good_style"
    id: Mapped[int] = mapped_column(sqlalchemy.types.Integer, primary_key=True, autoincrement=True)
    good_id: Mapped[int] = mapped_column(ForeignKey("good.id"))
    good: Mapped[Good] = relationship(back_populates="styles")
    name: Mapped[str] = mapped_column(sqlalchemy.types.String(256), nullable=False)
    description: Mapped[str] = mapped_column(sqlalchemy.types.String(512), nullable=True)
    image_id: Mapped[str] = mapped_column(sqlalchemy.types.String(256), nullable=True)
    price: Mapped[int] = mapped_column(sqlalchemy.types.Integer, nullable=False)
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="style")
    cart_items: Mapped[List["CartItem"]] = relationship(back_populates="style")
    created_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now,
                                                          onupdate=datetime.datetime.now)


class TagGoodLink(Base):
    __tablename__ = "tag_good_link"
    id: Mapped[int] = mapped_column(sqlalchemy.types.Integer, primary_key=True, autoincrement=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id"), primary_key=True)
    good_id: Mapped[int] = mapped_column(ForeignKey("good.id"), primary_key=True)
    tag: Mapped["Tag"] = relationship(back_populates="good_links")
    good: Mapped[Good] = relationship(back_populates="tag_links")
    created_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now,
                                                          onupdate=datetime.datetime.now)


class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(sqlalchemy.types.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(sqlalchemy.types.String(64), nullable=False)
    description: Mapped[str] = mapped_column(sqlalchemy.types.String(128), nullable=True)
    good_links: Mapped[List[TagGoodLink]] = relationship(back_populates="tag")
    created_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now,
                                                          onupdate=datetime.datetime.now)
