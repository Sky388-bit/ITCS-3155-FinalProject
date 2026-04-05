from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base

class Promotion(Base):
    __tablename__ = 'promotions'
    id = Column(Integer, primary_key=True)
    promotion_discount = Column(Integer, nullable=False)
    promotion_name = Column(String, nullable=False)