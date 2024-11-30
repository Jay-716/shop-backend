import datetime
from typing import Dict, List, Tuple

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, update, delete, func, column
from sqlalchemy.orm import Session
from redis import Redis

from app.db import get_session, get_redis
from app.auth import current_user, current_store
from app.models.good import Good
from app.models.order import OrderItem, Order
from app.models.user import User, Role, Address
from app.models.store import Store
from app.schemas.user import AddressRead
from app.schemas.good import GoodRead
from app.schemas.order import OrderItemFullRead
from app.schemas.store import StoreRead, StoreCreate, StoreUpdate, StoreProfile, StoreGoodProfile


store_router = APIRouter(prefix="/store", tags=["店铺"])
store_good_router = APIRouter(prefix="/sgood", tags=["商品", "店铺"])


@store_router.post("")
def create_store(store_dict: StoreCreate, user: User = Depends(current_user), db: Session = Depends(get_session))\
        -> StoreRead:
    store = Store(**store_dict.model_dump(exclude_none=True), owner_id=user.id)
    db.add(store)
    db.commit()
    db.refresh(store)
    return StoreRead.model_validate(store)


@store_router.get("")
def get_all_store(user: User = Depends(current_user), db: Session = Depends(get_session)) -> Page[StoreRead]:
    query = select(Store)
    if user.role != Role.Admin:
        query = query.where(Store.owner_id == user.id)
    return paginate(db, query)


@store_router.delete("/{store_id}")
def delete_store(store_id: int, user: User = Depends(current_user), db: Session = Depends(get_session)) -> Dict:
    query = delete(Store).where(Store.id == store_id)
    if user.role != Role.Admin:
        query = query.where(Store.owner_id == user.id)
    db.execute(query)
    db.commit()
    return {"message": "success"}


@store_router.put("/{store_id}")
def update_store(store_id: int, store_dict: StoreUpdate, user: User = Depends(current_user), db: Session = Depends(get_session)) -> StoreRead:
    store = db.get(Store, store_id)
    if not store or (user.role != Role.Admin and store.owner_id != user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Address not found.")
    query = update(Store).where(Store.id == store_id).values(store_dict.model_dump(exclude_none=True))
    db.execute(query)
    db.refresh(store)
    db.commit()
    return StoreRead.model_validate(store)


@store_good_router.get("")
def get_all_store_good(store: Store = Depends(current_store), db: Session = Depends(get_session)) -> Page[GoodRead]:
    query = select(Good).where(Good.store_id == store.id).order_by(Good.created_at.desc())
    return paginate(db, query)


@store_good_router.get("/orders/{good_id}")
def get_store_good_orders(good_id: int, store: Store = Depends(current_store), db: Session = Depends(get_session)) \
        -> Page[OrderItemFullRead]:
    query = (select(OrderItem)
             .join(Good, Good.id == OrderItem.good_id)
             .where(Good.store_id == store.id)
             .where(Good.id == good_id)
             .order_by(OrderItem.created_at.desc()))
    return paginate(db, query)


@store_good_router.get("/profile")
def get_store_profile(store: Store = Depends(current_store), db: Session = Depends(get_session)) -> StoreProfile:
    day_order_count = db.execute(
        select(func.count(OrderItem.id))
        .join(Good, Good.id == OrderItem.good_id)
        .where(Good.store_id == store.id)
        .where(func.extract("YEAR", OrderItem.created_at) == datetime.datetime.now().year)
        .where(func.extract("MONTH", OrderItem.created_at) == datetime.datetime.now().month)
        .where(func.extract("DAY", OrderItem.created_at) == datetime.datetime.now().day)
    ).scalar_one()
    month_order_count = db.execute(
        select(func.count(OrderItem.id))
        .join(Good, Good.id == OrderItem.good_id)
        .where(Good.store_id == store.id)
        .where(func.extract("YEAR", OrderItem.created_at) == datetime.datetime.now().year)
        .where(func.extract("MONTH", OrderItem.created_at) == datetime.datetime.now().month)
    ).scalar_one()
    day_total_price = db.execute(
        select(func.sum(OrderItem.count * OrderItem.price))
        .join(Good, Good.id == OrderItem.good_id)
        .where(Good.store_id == store.id)
        .where(func.extract("YEAR", OrderItem.created_at) == datetime.datetime.now().year)
        .where(func.extract("MONTH", OrderItem.created_at) == datetime.datetime.now().month)
        .where(func.extract("DAY", OrderItem.created_at) == datetime.datetime.now().day)
    ).scalar_one()
    month_total_price = db.execute(
        select(func.sum(OrderItem.count * OrderItem.price))
        .join(Good, Good.id == OrderItem.good_id)
        .where(Good.store_id == store.id)
        .where(func.extract("YEAR", OrderItem.created_at) == datetime.datetime.now().year)
        .where(func.extract("MONTH", OrderItem.created_at) == datetime.datetime.now().month)
    ).scalar_one()
    return StoreProfile(
        day_order_count=day_order_count if day_order_count else 0,
        month_order_count=month_order_count if month_order_count else 0,
        day_total_price=day_total_price if day_total_price else 0,
        month_total_price=month_total_price if month_total_price else 0
    )


@store_good_router.get("/profile/good")
def get_store_good_profile(good_id: int, store: Store = Depends(current_store), db: Session = Depends(get_session))\
        -> StoreGoodProfile:
    query = (select(func.cast(OrderItem.created_at, sqlalchemy.DATE).label("date"), func.count(OrderItem.id))
             .join(Good, Good.id == OrderItem.good_id)
             .where(Good.store_id == store.id)
             .where(Good.id == good_id)
             .group_by("date")
             .order_by(column("date").desc()))
    timeline = db.execute(query).all()
    day_good_count = db.execute(
        select(func.sum(OrderItem.count))
        .where(Good.id == good_id)
        .where(Good.store_id == store.id)
        .where(func.extract("YEAR", OrderItem.created_at) == datetime.datetime.now().year)
        .where(func.extract("MONTH", OrderItem.created_at) == datetime.datetime.now().month)
        .where(func.extract("DAY", OrderItem.created_at) == datetime.datetime.now().day)
    ).scalar_one()
    month_good_count = db.execute(
        select(func.sum(OrderItem.count))
        .where(Good.id == good_id)
        .where(Good.store_id == store.id)
        .where(func.extract("YEAR", OrderItem.created_at) == datetime.datetime.now().year)
        .where(func.extract("MONTH", OrderItem.created_at) == datetime.datetime.now().month)
    ).scalar_one()
    return StoreGoodProfile(
        day_count=day_good_count if day_good_count else 0,
        month_count=month_good_count if month_good_count else 0,
        timeline=timeline
    )


@store_good_router.put("/send")
def send_store_good(order_item_id: int, store: Store = Depends(current_store),
                    db: Session = Depends(get_session), rdb: Redis = Depends(get_redis)) -> bool:
    order_item = db.get(OrderItem, order_item_id)
    if not order_item or order_item.good.store_id != store.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order item not found.")
    rdb.set(f"order_item_{order_item_id}", 1)
    order = db.get(Order, order_item.order_id)
    if all(rdb.get(f"order_item_{o.id}") for o in order.order_items):
        order.status = 2
        db.commit()
    return True


@store_good_router.get("/status")
def get_order_item_status(order_item_id: int, store: Store = Depends(current_store),
                          db: Session = Depends(get_session), rdb: Redis = Depends(get_redis)) -> bool:
    order_item = db.get(OrderItem, order_item_id)
    if not order_item or order_item.good.store_id != store.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order item not found.")
    if rdb.get(f"order_item_{order_item_id}") == 1:
        return True
    else:
        return False


@store_good_router.get("/address")
def get_order_item_address(order_item_id: int, store: Store = Depends(current_store),
                           db: Session = Depends(get_session)) -> AddressRead:
    order_item = db.get(OrderItem, order_item_id)
    if not order_item or order_item.good.store_id != store.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order item not found.")
    return AddressRead.model_validate(order_item.order.address)
