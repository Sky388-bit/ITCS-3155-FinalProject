from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field



class RatingBase(BaseModel):
    customer_id: Optional[int] = None
    rating: Optional[int] = None
    review_text: Optional[str] = None


class RatingsCreate(RatingBase):
    pass


class RatingsUpdate(BaseModel):
    customer_id: Optional[int] = None
    rating: Optional[int] = None
    review_text: Optional[str] = None


class Ratings(RatingBase):
    id: int
    rating_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
