import asyncio
from logging import getLogger
from database.postgres import Postgres
from scrapy import signals
from itemadapter import ItemAdapter

from database.services.article_service import crawler_db_mapping
from database.schema.base import Base

logger = getLogger(f"scrapy.{__name__}")

class PostgresPipeline:
    def __init__(self, uri, buffer_limit=100):
        self.postgres = Postgres(uri=uri)
        # Bulk insert articles instead of one by one.
        self.article_buffer = []
        # Buffer length. 0 for unlimited. All will be inserted at once at the end.
        self.buffer_limit = buffer_limit
        logger.debug("PostgresPipeline init buffer limit %d", self.buffer_limit)

    @classmethod
    def from_crawler(cls, crawler):
        pg_settings = crawler.settings.get("POSTGRES_PIPELINE_SETTINGS", {})
        postgres = cls(pg_settings.get("URI"), pg_settings.get("BUFFER_SIZE", 100))
        crawler.signals.connect(postgres.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(postgres.spider_closed, signal=signals.spider_closed)
        return postgres

    async def spider_opened(self, spider):
        await self.postgres.init_db(Base.metadata)
        self.DBService = crawler_db_mapping[spider.name]
        logger.info(
            "Postgres Pipeline use %s for DB service", self.DBService.__name__
        )

    async def spider_closed(self):
        await self.upsert_current_to_db()
        logger.debug("Done upserting final objects to db.")
        await self.postgres.close_db()

    async def process_item(self, item, spider):
        self.article_buffer.append(item)
        if self.buffer_limit != 0 and len(self.article_buffer) >= self.buffer_limit:
            await self.upsert_current_to_db()
        return item

    async def upsert_current_to_db(self):
        # Do upsert
        dict_list = []
        identifier_set = set()
        for article in self.article_buffer:
            insert_obj = dict(ItemAdapter(article))
            # Ignore identifier from news site. Might change.
            identifier = insert_obj.pop("identifier")
            # Prevent duplicate update.
            if not identifier in identifier_set:
                identifier_set.add(identifier)
                dict_list.append(insert_obj)

        async with self.postgres.engine.connect() as db_conn:
            await self.DBService.bulk_upsert(db_conn, dict_list)
        logger.info("Upserted %d items to db", len(dict_list))
        # Reset buffer
        self.article_buffer = []
