import enum
from sqlalchemy import Column, String, Integer, Enum, DateTime

from .base import Base

class ItemType(enum.Enum):
    video = 0
    article = 1

class VnExpress(Base):
    """
    Schema for saving article in to Postgres.
    """
    article_id = Column(String(10), nullable=False)
    article_type = Column(Integer, nullable=False)
    category_id = Column(String(10), nullable=False)

class TuoiTre(Base):
    """
    Schema for saving article in to Postgres.
    """
    category = Column(String(256), nullable=False)
    item_type = Column(Enum(ItemType), nullable=False, default=ItemType.article)
    published_time = Column(DateTime(timezone=True), nullable=False)