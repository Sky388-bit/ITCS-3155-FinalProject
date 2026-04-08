from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base

class MenuItems(Base):
    __tablename__ = 'menu_items'
    id = Column(Integer, primary_key=True)
    dish_name = Column(String(20))
    dish_description = Column(String(20))
    #ingredients = relationship("Ingredients", back_populates="menu")
    price = Column(DECIMAL(10,2))
    calories = Column(Integer)
    category = Column(String(20))

