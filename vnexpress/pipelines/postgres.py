import asyncio
from logging import getLogger
from database.postgres import Postgres
from itemadapter import ItemAdapter

from database.services.article_service import ArticleService
from database.schema.base import Base

logger = getLogger(f"scrapy.{__name__}")

class PostgresPipeline:
    def __init__(self):
        self.postgres = Postgres(
            host="localhost",
            port=5432,
            user="postgres",
            password="postgres",
            database="postgres"
        )
        # Bulk insert articles instead of one by one.
        self.article_buffer = []
        # Buffer length. 0 for unlimited. All will be inserted at once at the end.
        self.buffer_limit = 100

    def open_spider(self, spider):
        initdb = self.postgres.init_db(Base.metadata)
        asyncio.get_event_loop().run_until_complete(initdb)

    def close_spider(self, spider):
        upsert_rest = self.upsert_current_to_db()
        asyncio.get_running_loop.run_until_complete(upsert_rest)
        close_pg = self.postgres.close_session()
        asyncio.get_running_loop.run_until_complete(close_pg)

    async def process_item(self, item, spider):
        self.article_buffer.append(item)
        if self.buffer_limit != 0 and len(self.article_buffer) >= self.buffer_limit:
            await self.upsert_current_to_db()
        return item

    async def upsert_current_to_db(self):
        # Do upsert
        dict_list = []
        for article in self.article_buffer:
            insert_obj = dict(ItemAdapter(article)) 
            insert_obj.pop("full_identifier")
            dict_list.append(insert_obj)

        async with self.postgres.engine.connect() as db_conn:
            await ArticleService.bulk_upsert(db_conn, dict_list)
        logger.info("Upserted %d items to db", len(dict_list))
        # Reset buffer
        self.article_buffer = []
