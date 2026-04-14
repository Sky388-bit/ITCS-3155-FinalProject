from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field



class RatingsBase(BaseModel):
    customers_id: int
    customers_name: str
    review_text: str
    rating: int


class RatingsCreate(RatingsBase):
    pass


class RatingsUpdate(BaseModel):
    customers_id: int
    customers_name: str
    review_text: str
    rating: int


class Ratings(RatingsBase):
    id: int
    rating_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
