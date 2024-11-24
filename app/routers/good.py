from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

from db import get_session
from auth import current_user
from app.models.user import User, Role
from app.models.store import Store
from app.models.good import Good, GoodDetail, GoodStyle
from app.schemas.good import *


good_router = APIRouter(prefix="/good", tags=["商品"])


@good_router.post("")
def create_good(good_dict: GoodCreate, user: User = Depends(current_user), db: Session = Depends(get_session))\
        -> GoodRead:
    store = db.get(Store, good_dict.store_id)
    if not store or (user.role != Role.Admin and store.owner_id != user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Store not found.")
    good = Good(**good_dict.model_dump(exclude_none=True))
    db.add(good)
    db.commit()
    db.refresh(good)
    return GoodRead.model_validate(good)


@good_router.get("")
def get_all_good(user: User = Depends(current_user), db: Session = Depends(get_session)) -> Page[GoodRead]:
    query = select(Good).join(Store, Store.id == Good.store_id)
    if user.role != Role.Admin:
        query = query.where(Store.owner_id == user.id)
    return paginate(db, query)


@good_router.delete("/{good_id}")
def delete_good(good_id: int, user: User = Depends(current_user), db: Session = Depends(get_session)) -> Dict:
    good = db.get(Good, good_id)
    if user.role != Role.Admin and good.store.owner_id != user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Good not found.")
    query = delete(GoodStyle).where(GoodStyle.good_id == good_id)
    db.execute(query)
    query = delete(GoodDetail).where(GoodDetail.good_id == good_id)
    db.execute(query)
    query = delete(Good).where(Good.id == good_id)
    db.execute(query)
    db.commit()
    return {"message": "success"}


@good_router.put("/{good_id}")
def update_good(good_id: int, good_dict: GoodUpdate, user: User = Depends(current_user),
                db: Session = Depends(get_session)) -> GoodRead:
    good = db.get(Good, good_id)
    if not good or (user.role != Role.Admin and good.store.owner_id != user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Good not found.")
    query = update(Good).where(Good.id == good_id).values(good_dict.model_dump(exclude_none=True))
    db.execute(query)
    db.refresh(good)
    db.commit()
    return GoodRead.model_validate(good)


@good_router.get("/{good_id}", dependencies=[Depends(current_user)])
def get_full_good(good_id: int, db: Session = Depends(get_session)) -> GoodFullRead:
    query = select(Good).where(Good.id == good_id)
    good = db.execute(query).scalar_one_or_none()
    if not good:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Good not found.")
    return GoodFullRead.model_validate(good)


@good_router.post("/full")
def create_full_good(good_dict: GoodFullCreate, user: User = Depends(current_user), db: Session = Depends(get_session))\
        -> GoodFullRead:
    store = db.get(Store, good_dict.store_id)
    if not store or (user.role != Role.Admin and store.owner_id != user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Store not found.")
    good = Good(**good_dict.model_dump(exclude_none=True, exclude={"details", "styles"}))
    db.add(good)
    db.flush()
    db.refresh(good)
    for detail in good_dict.details:
        detail_model = GoodDetail(**detail.model_dump(exclude_none=True), good_id=good.id)
        db.add(detail_model)
    for style in good_dict.styles:
        style_model = GoodStyle(**style.model_dump(exclude_none=True), good_id=good.id)
        db.add(style_model)
    db.flush()
    db.commit()
    db.refresh(good)
    return GoodFullRead.model_validate(good)


@good_router.put("/full/{good_id}")
def update_full_good(good_id: int, good_dict: GoodFullUpdate, user: User = Depends(current_user),
                     db: Session = Depends(get_session)) -> GoodFullRead:
    good = db.get(Good, good_id)
    if not good or (user.role != Role.Admin and good.store.owner_id != user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Good not found.")
    query = update(Good).where(Good.id == good_id).values(
        **good_dict.model_dump(exclude_none=True, exclude={"details", "styles"}))
    db.execute(query)
    db.refresh(good)
    query = delete(GoodDetail).where(GoodDetail.good_id == good_id)
    db.execute(query)
    for detail in good_dict.details:
        detail_model = GoodDetail(**detail.model_dump(exclude_none=True), good_id=good_id)
        db.add(detail_model)
    query = delete(GoodStyle).where(GoodStyle.good_id == good_id)
    db.execute(query)
    for style in good_dict.styles:
        style_model = GoodStyle(**style.model_dump(exclude_none=True), good_id=good_id)
        db.add(style_model)
    db.flush()
    db.commit()
    db.refresh(good)
    return GoodFullRead.model_validate(good)
