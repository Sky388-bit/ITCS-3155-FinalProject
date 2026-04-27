from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from .menu import Menu


class OrderDetailBase(BaseModel):
    amount: int


class OrderDetailCreate(OrderDetailBase):
    order_id: int
    menu_id: int

class OrderDetailUpdate(BaseModel):
    order_id: Optional[int] = None
    menu_id: Optional[int] = None
    amount: Optional[int] = None


class OrderDetail(OrderDetailBase):
    id: int
    order_id: int
    menu_id: int
    menu: Optional[Menu] = None

    model_config = ConfigDict(from_attributes=True)