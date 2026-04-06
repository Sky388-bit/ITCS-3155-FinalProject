from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from .order_details import OrderDetail



class OrderBase(BaseModel):
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    tracking_number: str
    order_status: str
    description: Optional[str] = None
    total_price: Optional[float] = None


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    customer_id: Optional[int] = None
    customer_name: Optional[str] = None
    tracking_number: Optional[str] = None
    order_status: Optional[str] = None
    description: Optional[str] = None
    total_price: Optional[float] = None


class Order(OrderBase):
    id: int
    order_date: Optional[datetime] = None
    order_details: list[OrderDetail] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
