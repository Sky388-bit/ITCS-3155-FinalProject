from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base

class Rating(Base):
    __tablename__ = 'ratings'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.id'))

    review_text = Column(String(300), nullable=False)
    rating = Column(Integer, nullable=False)

