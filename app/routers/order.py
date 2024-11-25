from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, update, delete

from db import get_session
from auth import current_user
from app.models.user import User, Role
from app.models.good import Good
from app.models.order import CartItem, Order, OrderItem
from app.schemas.order import *


order_router = APIRouter(prefix="/order", tags=["订单"])


@order_router.get("/cart")
def get_all_cart_item(user: User = Depends(current_user), db: Session = Depends(get_session)) -> Page[CartItemRead]:
    query = select(CartItem).options(joinedload(CartItem.good)).where(CartItem.user_id == user.id)
    return paginate(db, query)


@order_router.put("/cart")
def create_cart_item(cart_dict: CartItemCreate, user: User = Depends(current_user),
                     db: Session = Depends(get_session)) -> CartItemRead:
    good = db.get(Good, cart_dict.good_id)
    if not good:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Good not found.")
    cart_item = CartItem(user_id=user.id, good_id=good.id, style_id=cart_dict.style_id)
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return CartItemRead.model_validate(cart_item)


@order_router.delete("/cart/{cart_item_id}")
def delete_cart_item(cart_item_id: int, user: User = Depends(current_user), db: Session = Depends(get_session)) \
        -> Dict:
    cart_item = db.get(CartItem, cart_item_id)
    if not cart_item or (user.role != Role.Admin and cart_item.user_id != user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart item not found.")
    db.delete(cart_item)
    db.commit()
    return {"message": "success"}


@order_router.get("")
def get_all_order(user: User = Depends(current_user), db: Session = Depends(get_session)) -> Page[OrderRead]:
    query = select(Order)
    if user.role != Role.Admin:
        query = query.where(Order.user_id == user.id)
    return paginate(db, query)


def _create_order_items(order_goods: List[OrderItemFullCreate], order_id: int, goods: Dict[int, Good])\
        -> List[OrderItem]:
    order_items = []
    for item in order_goods:
        curr_good = goods[item.good_id]
        curr_styles = dict(map(lambda s: (s.id, s), curr_good.styles))
        if item.style_id and item.style_id not in curr_styles.keys():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Style not found.")
        order_item = OrderItem(order_id=order_id, good_id=item.good_id, style_id=item.style_id, count=item.count,
                               price=curr_styles[item.style_id].price if item.style_id else curr_good.price)
        order_items.append(order_item)
    return order_items


@order_router.post("/full")
def create_order(order_dict: OrderFullCreate, user: User = Depends(current_user), db: Session = Depends(get_session))\
        -> OrderFullRead:
    good_id_set = set(map(lambda g: g.good_id, order_dict.goods))
    query = (select(Good)
             .options(joinedload(Good.styles))
             .where(Good.id.in_(good_id_set)))
    goods = db.execute(query).unique().scalars().all()
    if len(goods) != len(good_id_set):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Good not found.")
    good_map = dict(map(lambda g: (g.id, g), goods))
    order_items = _create_order_items(order_dict.goods, 0, good_map)
    order = Order(**order_dict.model_dump(exclude={"goods"}), user_id=user.id)
    order.total_price = sum(map(lambda o: o.price * o.count, order_items))
    db.add(order)
    db.flush()
    db.refresh(order)
    for order_item in order_items:
        order_item.order_id = order.id
    db.bulk_save_objects(order_items)
    db.commit()
    db.refresh(order)
    return OrderFullRead.model_validate(order)


@order_router.delete("/{order_id}")
def delete_order(order_id: int, user: User = Depends(current_user), db: Session = Depends(get_session)) -> Dict:
    order = db.get(Order, order_id)
    if not order or (user.role != Role.Admin and order.user_id != user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order not found.")
    query = delete(OrderItem).where(OrderItem.order_id == order_id)
    db.execute(query)
    db.flush()
    query = delete(Order).where(Order.id == order_id)
    db.execute(query)
    db.flush()
    db.commit()
    return {"message": "success"}


@order_router.get("/{order_id}")
def get_full_order(order_id: int, user: User = Depends(current_user), db: Session = Depends(get_session)) \
        -> OrderFullRead:
    order = db.get(Order, order_id)
    if not order or (user.role != Role.Admin and order.user_id != user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order not found.")
    return OrderFullRead.model_validate(order)


@order_router.put("/{order_id}")
def update_full_order(order_id: int, order_dict: OrderFullUpdate, user: User = Depends(current_user),
                      db: Session = Depends(get_session)) -> OrderFullRead:
    order = db.get(Order, order_id)
    if not order or (user.role != Role.Admin and order.user_id != user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order not found.")
    query = (update(Order).where(Order.id == order_id)
             .values(**order_dict.model_dump(exclude_none=True, exclude={"goods"})))
    db.execute(query)
    db.refresh(order)
    query = delete(OrderItem).where(OrderItem.order_id == order_id)
    db.execute(query)
    good_id_set = set(map(lambda g: g.good_id, order_dict.goods))
    query = (select(Good)
             .options(joinedload(Good.styles))
             .where(Good.id.in_(good_id_set)))
    goods = db.execute(query).unique().scalars().all()
    good_map = dict(map(lambda g: (g.id, g), goods))
    order_items = _create_order_items(order_dict.goods, order.id, good_map)
    order.total_price = sum(map(lambda o: o.price * o.count, order_items))
    db.bulk_save_objects(order_items)
    db.flush()
    db.commit()
    db.refresh(order)
    return OrderFullRead.model_validate(order)