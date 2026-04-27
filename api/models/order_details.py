from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from ..dependencies.database import Base

class OrderDetail(Base):
    __tablename__ = "order_details"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    menu_id = Column(Integer, ForeignKey("menu.id"))
    amount = Column(Integer, index=True, nullable=False)


    order = relationship("Order", back_populates="order_details")
    menu = relationship("Menu", back_populates="order_details")
