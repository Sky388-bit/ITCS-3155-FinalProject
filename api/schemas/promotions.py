from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field



class PromotionsBase(BaseModel):
    promotions_discount: int
    promotions_name: str


class PromotionsCreate(PromotionsBase):
    pass


class PromotionsUpdate(BaseModel):
    promotions_discount: int
    promotions_name: str


class Promotions(PromotionsBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
