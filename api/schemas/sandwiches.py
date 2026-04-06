from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SandwichBase(BaseModel):
    sandwich_name: str
    price: float


class SandwichCreate(SandwichBase):
    pass


class SandwichUpdate(BaseModel):
    sandwich_name: Optional[str] = None
    price: Optional[float] = None


class Sandwich(SandwichBase):
    id: int

    model_config = ConfigDict(from_attributes=True)