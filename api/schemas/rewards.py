from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class RewardBase(BaseModel):
    points_earned: int
    reward_type: str  # 'purchase', 'birthday', 'redemption'


class RewardCreate(RewardBase):
    customer_id: int
    order_id: Optional[int] = None


class Reward(RewardBase):
    id: int
    customer_id: int
    order_id: Optional[int] = None
    created_date: datetime
    is_redeemed: bool = False
    redemption_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
