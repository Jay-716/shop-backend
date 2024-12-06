import datetime
from typing import List

import sqlalchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .user import User


class Notification(Base):
    __tablename__ = "notification"
    id: Mapped[int] = mapped_column(sqlalchemy.types.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped[User] = relationship("User", back_populates="notifications")
    title: Mapped[str] = mapped_column(sqlalchemy.types.String(256), nullable=False)
    content: Mapped[str] = mapped_column(sqlalchemy.types.String(512), nullable=True)
    read_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now)
    updated_at: Mapped[datetime.datetime] = mapped_column(sqlalchemy.types.DateTime, nullable=False,
                                                          insert_default=datetime.datetime.now,
                                                          onupdate=datetime.datetime.now)

