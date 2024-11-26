from pydantic import BaseModel, ConfigDict

from .user import UserRead
from .order import OrderRead


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    seq: str
    user_id: int
    order_id: int
    service_id: int
    amount: int
    status: int


class PaymentFullRead(PaymentRead):
    user: UserRead
    order: OrderRead


class PaymentCreate(BaseModel):
    order_id: int
    service_id: int
