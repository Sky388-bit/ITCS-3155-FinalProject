from typing import Optional
from pydantic import BaseModel, ConfigDict


class CustomersBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class CustomersCreate(CustomersBase):
    pass


class CustomersUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class Customers(CustomersBase):
    id: int

    model_config = ConfigDict(from_attributes=True)