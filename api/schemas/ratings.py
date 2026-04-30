from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field



class RatingsBase(BaseModel):
    customers_id: int
    menu_id: int
    customers_name: str
    review_text: str
    rating: int


class RatingsCreate(RatingsBase):
    pass


class RatingsUpdate(BaseModel):
    customers_id: Optional[int] = None
    menu_id: Optional[int] = None
    customers_name: Optional[str] = None
    review_text: Optional[str] = None
    rating: Optional[int] = None


class Ratings(RatingsBase):
    id: int
    rating_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
