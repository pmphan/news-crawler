from sqlalchemy import Column, String, Integer

from .base import Base

class Articles(Base):
    """
    Schema for saving article in to Postgres.
    """
    url = Column(String(256), index=True, nullable=False, unique=True)
    title = Column(String(256), nullable=False)
    article_id = Column(String(10), nullable=False)
    article_type = Column(Integer, nullable=False)
    category_id = Column(String(10), nullable=False)
    score = Column(Integer, index=True, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)