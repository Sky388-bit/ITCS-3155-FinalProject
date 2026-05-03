from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base

class Customers(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(15))
    address = Column(String(100))
    password = Column(String(255), nullable=False)
    birthday = Column(Date, nullable=True)
    reward_points = Column(Integer, default=0)
    orders = relationship("Order", back_populates="customers")
    favorite_orders = relationship("FavoriteOrder", back_populates="customer")
    #order_history = relationship("OrderHistory", back_populates="customers")