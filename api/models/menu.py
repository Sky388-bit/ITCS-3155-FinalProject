from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base

class Menu(Base):
    __tablename__ = 'menu'
    id = Column(Integer, primary_key=True)
    dish_name = Column(String(100))
    dish_description = Column(String(200))
    #recipes = relationship("Recipe", back_populates="menu")
    price = Column(DECIMAL(10,2))
    calories = Column(Integer)
    category = Column(String(20))

    order_details = relationship("OrderDetail", back_populates="menu")
    recipes = relationship("Recipe", back_populates="menu")

