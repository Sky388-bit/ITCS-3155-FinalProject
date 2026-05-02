from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field



class PromotionsBase(BaseModel):
    promotions_discount: int
    promotions_name: str
    expiration_date: Optional[datetime] = None


class PromotionsCreate(PromotionsBase):
    pass


class PromotionsUpdate(BaseModel):
    promotions_discount: Optional[int] = None
    promotions_name: Optional[str] = None
    expiration_date: Optional[datetime] = None


class Promotions(PromotionsBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
