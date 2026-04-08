from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field



class RatingBase(BaseModel):
    customer_id: int
    review_text: str
    rating: int


class RatingsCreate(RatingBase):
    pass


class RatingsUpdate(BaseModel):
    customer_id: int
    review_text: str
    rating: int


class Ratings(RatingBase):
    id: int
    rating_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
