from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class FavoriteOrderBase(BaseModel):
    customer_id: int
    order_id: int


class FavoriteOrderCreate(FavoriteOrderBase):
    pass


class FavoriteOrder(FavoriteOrderBase):
    id: int
    added_date: datetime

    model_config = ConfigDict(from_attributes=True)
