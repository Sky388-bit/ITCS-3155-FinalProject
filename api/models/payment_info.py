from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base

class PaymentInfo(Base):
    __tablename__ = "payment_info"
    id = Column(Integer, primary_key=True)
    transaction_status = Column(String(20))
    payment_type = Column(String(20))
    order_detail_id = Column(Integer, ForeignKey("order_details.id"))
    order_details = relationship("OrderDetail", back_populates="payment_details")