from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import date


class CustomersBase(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    birthday: Optional[date] = None


class CustomersCreate(CustomersBase):
    password: str


class CustomersUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    birthday: Optional[date] = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class Customers(CustomersBase):
    id: int
    reward_points: int = 0

    model_config = ConfigDict(from_attributes=True)