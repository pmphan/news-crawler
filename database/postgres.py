from logging import getLogger

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

logger = getLogger(f"scrapy.{__name__}")


class Postgres:

    def __init__(self, user, password, database, host="localhost", port=5432):
        self.uri = "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            user,
            password,
            host,
            port,
            database
        )
        self.engine = create_async_engine(self.uri)
        logger.info("Postgres URI: %s", self.uri)

    async def close_db(self):
        logger.debug("Postgres engine disposed.")
        await self.engine.dispose()

    async def init_db(self, metadata):
        """
        Create all database specified in metadata.

        Args:
            metadata: Create tables specified in here.
        """
        async with self.engine.begin() as conn:
            #await conn.run_sync(metadata.drop_all)
            await conn.run_sync(metadata.create_all)
            logger.debug("Created all tables: %s", metadata.tables.keys())