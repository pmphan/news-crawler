from crawlers.vnexpress_crawler import VnExpressCrawler
from parsers.comment_parser import CommentParser
from database.postgres import Postgres
from schema.postgres import Base
from database.article_service import ArticleService

class PipelineManager:
    def __init__(self, config={}):
        self.crawler = VnExpressCrawler(days_ago=7, buffer_limit=25)
        self.parser = CommentParser()

        if "postgres" in config:
            self.postgres = Postgres(config["postgres"])
        else:
            raise ValueError(
                "[db] Expected 'postgres' in configuration dict but found None.")

    async def init_db(self):
        self.postgres.init_session()
        await self.postgres.init_db(Base.metadata)

    async def start(self):
        async for article_list in self.crawler.start():
            parser_result = await self.parser.start(article_list)

            async with self.postgres as db_conn:
                result = await ArticleService.bulk_upsert(db_conn, parser_result)