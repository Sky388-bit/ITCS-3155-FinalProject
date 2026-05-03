from sqlalchemy import Column, ForeignKey, Integer, String, DATETIME, text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    points_earned = Column(Integer, nullable=False)
    reward_type = Column(String(50), nullable=False)  # 'purchase', 'birthday', 'redemption'
    created_date = Column(DATETIME, nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    is_redeemed = Column(Boolean, default=False)
    redemption_date = Column(DATETIME, nullable=True)

    customer = relationship("Customers")
    order = relationship("Order")
