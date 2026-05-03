from sqlalchemy import Column, ForeignKey, Integer, DATETIME, text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base


class FavoriteOrder(Base):
    __tablename__ = "favorite_orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    added_date = Column(DATETIME, nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    customer = relationship("Customers", back_populates="favorite_orders")
    order = relationship("Order")
