from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from .order_details import OrderDetail



class OrderBase(BaseModel):
    customers_id: Optional[int] = None
    customers_name: Optional[str] = None
    tracking_number: Optional[str] = None
    order_status: Optional[str] = None
    description: Optional[str] = None
    total_price: Optional[float] = None
    order_type: Optional[str] = None
    customers_email: Optional[str] = None
    customers_phone: Optional[str] = None


class OrderCreate(OrderBase):
    promo_code: Optional[str] = None


class OrderUpdate(BaseModel):
    customers_id: Optional[int] = None
    customers_name: Optional[str] = None
    tracking_number: Optional[str] = None
    order_status: Optional[str] = None
    description: Optional[str] = None
    total_price: Optional[float] = None
    order_type: Optional[str] = None
    customers_email: Optional[str] = None
    customers_phone: Optional[str] = None


class Order(OrderBase):
    id: int
    order_date: Optional[datetime] = None
    order_details: list[OrderDetail] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
