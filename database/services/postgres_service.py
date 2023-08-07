from logging import getLogger
from typing import Generic, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.functions import current_timestamp

from sqlalchemy.ext.asyncio import AsyncSession

from database.schema.base import Base

TableType = TypeVar("TableType", bound=Base)

logger = getLogger(f"scrapy.{__name__}")

class BasePostgresService(Generic[TableType]):
    """
    Base Postgres service.
    """
    model: Type[TableType]

    @classmethod
    async def get(cls, db: AsyncSession, _id: str) -> Optional[TableType]:
        return await db.get(cls.model, _id)

    @classmethod
    async def get_one(cls, db: AsyncSession, _filter: dict):
        query = select(cls.model).filter_by(**_filter)
        result = await db.execute(query)
        return result.first()

    @classmethod
    async def get_list(cls, db: AsyncSession, _filter: dict):
        query = select(cls.model).filter_by(**_filter)
        result = await db.execute(query)
        return result.all()

    @classmethod
    async def bulk_upsert(cls, db: AsyncSession, obj_list: list[dict]):
        """
        Utilize Postgres' ON CONFLICT DO UPDATE to bulk upsert items.
        """
        logger.debug("Upserting %d objects into db..." % len(obj_list))
        stmt = insert(cls.model).values(obj_list)
        stmt = stmt.on_conflict_do_update(
            index_elements=['url'],
            set_={
                "score": stmt.excluded.score,
                "update_time": current_timestamp()
            }
        )
        await db.execute(stmt)
        await db.commit()

    @classmethod
    async def get_all_article_ranked(cls, db: AsyncSession):
        query = select(cls.model).order_by(cls.model.score.desc())
        result = await db.execute(query)
        await db.commit()
        return result.fetchall()