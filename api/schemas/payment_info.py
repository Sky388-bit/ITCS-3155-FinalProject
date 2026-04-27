from typing import Optional
from pydantic import BaseModel, ConfigDict

class PaymentInfoBase(BaseModel):
    transaction_status: Optional[str] = None
    payment_type: Optional[str] = None
    amount: float
    order_id: int

class PaymentInfoCreate(PaymentInfoBase):
    pass

class PaymentInfoUpdate(PaymentInfoBase):
    transaction_status: Optional[str] = None
    payment_type: Optional[str] = None
    amount: Optional[float] = None

class PaymentInfo(PaymentInfoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)