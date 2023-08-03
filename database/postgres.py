from logging import getLogger

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

logger = getLogger(__name__)


class Postgres:

    def __init__(self, config: dict):
        self.init_config(config)

    def init_config(self, config: dict):
        self.uri = "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            config["user"],
            config["password"],
            config["host"],
            config["port"],
            config["database"]
        )
        self.engine = create_async_engine(self.uri)
        logger.info("Postgres URI: %s", self.uri)

    async def __aenter__(self):
        self.async_session = self.session()
        return self.async_session

    async def __aexit__(self, exc_type, exc, tb):
        await self.async_session.close()
        self.async_session = None

    def init_session(self):
        """
        Init Postgres async session
        """
        self.session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
        return self.session

    async def close_session(self):
        await self.session.close()

    async def init_db(self, metadata):
        """
        Create all database specified in metadata.

        Args:
            metadata: Create tables specified in here.
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(metadata.create_all)
            logger.debug("[db] Created all tables: %s", metadata.tables.keys())