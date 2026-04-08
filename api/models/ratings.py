from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base

class Ratings(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer_id'))
    review_text = Column(String(300))
    rating = Column(Integer)

