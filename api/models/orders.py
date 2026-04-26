from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customers_id = Column(Integer, ForeignKey("customers.id"))
    customers_name = Column(String(100))
    tracking_number = Column(String(100), nullable=False)
    order_status = Column(String(100), nullable=False)
    order_date = Column(DATETIME, nullable=False, server_default=str(datetime.now()))
    description = Column(String(300))
    total_price = Column(DECIMAL(10,2))
    order_type = Column(String(100), nullable=False)
    customers_email = Column(String(100))
    customers_phone = Column(String(15))

    customers = relationship("Customers", back_populates="orders")
    order_details = relationship("OrderDetail", back_populates="order")
    payment_details = relationship("PaymentInfo", back_populates="order")