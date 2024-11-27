import datetime
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, update, func

from app.db import get_session
from app.auth import current_user
from app.models import Address, User
from app.models.order import Order, OrderItem
from app.schemas.user import AddressRead, AddressCreate, AddressUpdate, Role, UserProfile


user_router = APIRouter(prefix="/user", tags=["用户"])
address_router = APIRouter(prefix="/address", tags=["收货地址"])


@address_router.post("")
def create_address(address_dict: AddressCreate, user: User = Depends(current_user), db: Session = Depends(get_session))\
        -> AddressRead:
    address = Address(**address_dict.model_dump(), user_id=user.id)
    db.add(address)
    db.commit()
    db.refresh(address)
    return AddressRead.model_validate(address)


@address_router.get("")
def get_all_address(user: User = Depends(current_user), db: Session = Depends(get_session)) -> Page[AddressRead]:
    query = select(Address)
    if user.role != Role.Admin:
        query = query.where(Address.user_id == user.id)
    return paginate(db, query)


@address_router.delete("/{address_id}")
def delete_address(address_id: int, user: User = Depends(current_user), db: Session = Depends(get_session)) -> Dict:
    query = delete(Address).where(Address.id == address_id)
    if user.role != Role.Admin:
        query = query.where(Address.user_id == user.id)
    db.execute(query)
    db.commit()
    return {"message": "success"}


@address_router.put("/{address_id}")
def update_address(address_id: int, address_dict: AddressUpdate, user: User = Depends(current_user),
                   db: Session = Depends(get_session)) -> AddressRead:
    address = db.get(Address, address_id)
    if not address or (user.role != Role.Admin and address.user_id != user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Address not found.")
    query = update(Address).where(Address.id == address_id).values(address_dict.model_dump(exclude_none=True))
    db.execute(query)
    db.refresh(address)
    db.commit()
    return AddressRead.model_validate(address)


@user_router.get("/profile", summary="用户汇总信息")
def get_user_profile(user: User = Depends(current_user), db: Session = Depends(get_session)) -> UserProfile:
    reg_days = (datetime.datetime.now() - user.created_at).days
    order_count = db.execute(
        select(func.count(Order.id)).
        where(Order.user_id == user.id)
    ).scalar_one()
    good_count = db.execute(
        select(func.sum(OrderItem.count))
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.user_id == user.id)
    ).unique().scalar_one()
    comment_count = 0
    first_order = db.execute(select(Order)
                             .where(Order.user_id == user.id)
                             .order_by(Order.created_at)
                             .limit(1)).scalar_one_or_none()
    first_receive = db.execute(select(Order)
                               .where(Order.user_id == user.id)
                               .where(Order.status == 3)
                               .order_by(Order.created_at)
                               .limit(1)).scalar_one_or_none()
    timeline = [("账号创建", user.created_at)]
    if first_order:
        timeline.append(("第一次购物", first_order.created_at))
    if first_receive:
        timeline.append(("第一次收货", first_receive.created_at))
    return UserProfile(
        reg_days=reg_days,
        order_count=order_count,
        good_count=good_count,
        comment_count=comment_count,
        timeline=timeline
    )
