import random
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete, func

from app.db import get_session
from app.auth import current_user, current_superuser
from app.models.user import User, Role
from app.models.store import Store
from app.models.good import Good, GoodDetail, GoodStyle, TagGoodLink, Tag
from app.schemas.good import *


good_router = APIRouter(prefix="/good", tags=["商品"])
tag_router = APIRouter(prefix="/tag", tags=["商品", "标签"])


@good_router.get("/random", dependencies=[Depends(current_user)], summary="主页获取随机商品")
def get_random_good(db: Session = Depends(get_session)) -> List[GoodRead]:
    total_good = db.execute(select(func.count(Good.id))).scalar_one()
    subquery = select(Good).offset(random.randint(1, max(total_good - 100, 1))).limit(100).subquery()
    query = select(subquery, func.random().label("_rand_num")).order_by("_rand_num")
    return db.execute(query).all()


@tag_router.get("/random", dependencies=[Depends(current_user)], summary="主页获取随机tag")
def get_random_tag(db: Session = Depends(get_session)) -> List[TagRead]:
    total_tag = db.execute(select(func.count(Tag.id))).scalar_one()
    subquery = select(Tag).offset(random.randint(1, max(total_tag - 50, 1))).limit(50).subquery()
    query = select(subquery, func.random().label("_rand_num")).order_by("_rand_num")
    return db.execute(query).all()


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
    tag_ids_set = set(good_dict.tag_ids)
    tags = db.execute(select(func.count(Tag.id)).where(Tag.id.in_(tag_ids_set))).scalar_one()
    if tags != len(tag_ids_set):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag not found.")
    good = Good(**good_dict.model_dump(exclude_none=True, exclude={"details", "styles", "tag_ids"}))
    db.add(good)
    db.flush()
    db.refresh(good)
    for detail in good_dict.details:
        detail_model = GoodDetail(**detail.model_dump(exclude_none=True), good_id=good.id)
        db.add(detail_model)
    for style in good_dict.styles:
        style_model = GoodStyle(**style.model_dump(exclude_none=True), good_id=good.id)
        db.add(style_model)
    for tag_id in tag_ids_set:
        tag = TagGoodLink(tag_id=tag_id, good_id=good.id)
        db.add(tag)
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
        **good_dict.model_dump(exclude_none=True, exclude={"details", "styles", "tag_ids"}))
    db.execute(query)
    db.refresh(good)
    if good_dict.tag_ids is not None:
        tag_ids_set = set(good_dict.tag_ids)
        tags = db.execute(select(func.count(Tag.id)).where(Tag.id.in_(tag_ids_set))).scalar_one()
        if tags != len(tag_ids_set):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag not found.")
        query = delete(TagGoodLink).where(TagGoodLink.good_id == good_id)
        db.execute(query)
        for tag_id in tag_ids_set:
            tag = TagGoodLink(tag_id=tag_id, good_id=good.id)
            db.add(tag)
    if good_dict.details is not None:
        query = delete(GoodDetail).where(GoodDetail.good_id == good_id)
        db.execute(query)
        for detail in good_dict.details:
            detail_model = GoodDetail(**detail.model_dump(exclude_none=True), good_id=good_id)
            db.add(detail_model)
    if good_dict.styles is not None:
        query = delete(GoodStyle).where(GoodStyle.good_id == good_id)
        db.execute(query)
        for style in good_dict.styles:
            style_model = GoodStyle(**style.model_dump(exclude_none=True), good_id=good_id)
            db.add(style_model)
    db.flush()
    db.commit()
    db.refresh(good)
    return GoodFullRead.model_validate(good)


@tag_router.post("", dependencies=[Depends(current_superuser)])
def create_tag(tag_dict: TagCreate, db: Session = Depends(get_session)) -> TagRead:
    tag = Tag(**tag_dict.model_dump(exclude_none=True))
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return TagRead.model_validate(tag)


@tag_router.get("", dependencies=[Depends(current_superuser)])
def get_all_tag(db: Session = Depends(get_session)) -> Page[TagRead]:
    query = select(Tag)
    return paginate(db, query)


@tag_router.delete("/{tag_id}", dependencies=[Depends(current_superuser)])
def delete_tag(tag_id: int, db: Session = Depends(get_session)) -> Dict:
    query = delete(TagGoodLink).where(TagGoodLink.tag_id == tag_id)
    db.execute(query)
    query = delete(Tag).where(Tag.id == tag_id)
    db.execute(query)
    db.commit()
    return {"message": "success"}
