from sqlalchemy import Column, String, Integer

from .base import Base

class VnExpress(Base):
    """
    Schema for saving article in to Postgres.
    """
    article_id = Column(String(10), nullable=False)
    article_type = Column(Integer, nullable=False)
    category_id = Column(String(10), nullable=False)