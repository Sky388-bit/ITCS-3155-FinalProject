from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base

class Promotions(Base):
    __tablename__ = 'promotions'
    id = Column(Integer, primary_key=True)
    promotions_discount = Column(Integer, nullable=False)
    promotions_name = Column(String(50), nullable=False)