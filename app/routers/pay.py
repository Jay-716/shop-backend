from secrets import token_hex
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.auth import current_user
from app.db import get_session
from app.models.order import Order
from app.models.pay import Payment
from app.models.user import User
from app.schemas.pay import PaymentRead, PaymentCreate


pay_router = APIRouter(prefix="/v1/pay", tags=["支付"])


@pay_router.get("/avail", dependencies=[Depends(current_user)], summary="获取可用支付方式")
def get_available_services() -> List[Dict]:
    return [
        {"id": 1, "name": "支付宝"},
        {"id": 2, "name": "微信支付"},
        {"id": 3, "name": "银联"},
    ]


@pay_router.post("/pay-order", summary="支付订单")
def pay_order(pay_dict: PaymentCreate, user: User = Depends(current_user),
              db: Session = Depends(get_session)) -> PaymentRead:
    order = db.get(Order, pay_dict.order_id)
    if not order or order.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order not found.")
    if db.execute(select(func.count(Payment.id)).where(Payment.order_id == pay_dict.order_id)).scalar_one() > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already payed.")
    # No discounts, no pay for others...
    payment = Payment(
        seq=token_hex(16).upper(),
        user_id=user.id,
        order_id=order.id,
        service_id=pay_dict.service_id,
        amount=order.total_price,
        status=1
    )
    db.add(payment)
    order.status = 1
    db.commit()
    db.refresh(payment)
    return PaymentRead.model_validate(payment)
