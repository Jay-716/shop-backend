import datetime
from typing import List

import sqlalchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .user import User


class Payment(Base):
    __tablename__ = "payment"
    id: Mapped[int] = mapped_column(sqlalchemy.types.Integer, primary_key=True, autoincrement=True)
    seq: Mapped[str] = mapped_column(sqlalchemy.types.String(128), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship(back_populates="payments")
    order_id: Mapped[int] = mapped_column(ForeignKey("order.id"))
    order: Mapped["Order"] = relationship(back_populates="payment")
    service_id: Mapped[int] = mapped_column(sqlalchemy.types.SmallInteger, nullable=False)
    amount: Mapped[int] = mapped_column(sqlalchemy.types.Integer, nullable=False)
    status: Mapped[int] = mapped_column(sqlalchemy.types.SmallInteger, nullable=False, default=0)
    created_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now,
                                                          onupdate=datetime.datetime.now)
