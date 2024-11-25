from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Session

from app.db import get_session
from app.auth import current_user
from app.models.user import User, Role
from app.models.store import Store
from app.schemas.store import StoreRead, StoreCreate, StoreUpdate


store_router = APIRouter(prefix="/store", tags=["店铺"])


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
