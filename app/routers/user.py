from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, update

from db import get_session
from auth import current_user
from app.models import Address, User
from app.schemas.user import AddressRead, AddressCreate, AddressUpdate, Role


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
