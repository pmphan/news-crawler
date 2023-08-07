from sqlalchemy import Column, Identity, BigInteger, String, Integer, DateTime
from sqlalchemy.orm import registry, declared_attr
from sqlalchemy.sql.functions import current_timestamp

class_registry = registry()

@class_registry.as_declarative_base()
class Base(object):
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    id = Column(BigInteger, Identity(always=True), primary_key=True)
    create_time = Column(DateTime(timezone=True), server_default=current_timestamp())
    update_time = Column(DateTime(timezone=True), server_default=current_timestamp(), onupdate=current_timestamp())
    url = Column(String(256), index=True, nullable=False, unique=True)
    title = Column(String(256), nullable=False)
    score = Column(Integer, index=True, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
