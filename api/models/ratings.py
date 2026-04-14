from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base

class Ratings(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True)
    customers_id = Column(Integer, ForeignKey('customers.id'))
    #customers_id = Column(Integer)
    customers_name = Column(String(100))
    review_text = Column(String(300))
    rating = Column(Integer)

