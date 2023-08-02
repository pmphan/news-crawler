from sqlalchemy import Column, Identity, String, Integer, BigInteger, DateTime
from sqlalchemy.orm import registry, declared_attr
from sqlalchemy.sql.functions import current_timestamp

class_registry = registry()

@class_registry.as_declarative_base()
class Base(object):
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id = Column(Integer, Identity(always=True), primary_key=True)
    create_time = Column(DateTime(timezone=True), server_default=current_timestamp())
    update_time = Column(DateTime(timezone=True), server_default=current_timestamp(), onupdate=current_timestamp())

class Articles(Base):
    """
    Schema for saving article in to Postgres.
    """
    url = Column(String(256), index=True, nullable=False, unique=True)
    title = Column(String(256), nullable=False)
    article_id = Column(String(10), nullable=False, unique=True)
    article_type = Column(Integer, nullable=False)
    category_id = Column(String(10), nullable=False)
    score = Column(Integer, nullable=False, default=0)