from logging import getLogger
from crawlers.vnexpress_crawler import VnExpressCrawler
from parsers.comment_parser import CommentParser
from database.postgres import Postgres
from schema.postgres import Base
from database.article_service import ArticleService

logger = getLogger(__name__)

class Singleton (type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class PipelineManager(metaclass=Singleton):
    def __init__(self, config):
        self.config = config

    async def init_services(self):
        """
        Init all needed services.
        """
        await self.init_db(self.config)

        self.parser = CommentParser()

        if "crawler" in self.config:
            logger.info("[crawler] Initing VnExpress crawler.")
            crawler_config = self.config["crawler"]
            self.init_crawler(crawler_config)
        else:
            raise ValueError(
                "[config] Expected 'crawler' in configuration dict but found None.")

    def init_crawler(self, crawler_config):
        """
        Init crawler with config from config file.
        """
        days_ago = crawler_config["days_ago"]

        if crawler_config["name"] and crawler_config["name"] == "vnexpress":
            buffer_limit = crawler_config["buffer_limit"]
            self.crawler = VnExpressCrawler(days_ago=days_ago, buffer_limit=buffer_limit)
        else:
            raise ValueError(
                f"[config] Crawler \'{crawler_config['name']}\' not supported.")

    async def init_db(self, config):
        """
        Start connection to db and create all database.
        """
        logger.info("[db] Initing DB.")
        if "postgres" in config:
            self.postgres = Postgres(config["postgres"])
            self.postgres.init_session()
            await self.postgres.init_db(Base.metadata)
        else:
            raise ValueError(
                "[config] Expected 'postgres' in configuration dict but found None.")

    async def start(self):
        """
        Start the pipeline.
        """
        async for article_list in self.crawler.start():
            parser_result = await self.parser.start(article_list)

            # Save output to db
            async with self.postgres as db_conn:
                result = await ArticleService.bulk_upsert(db_conn, parser_result)

    async def get_ranked_result(self, output=None):
        """
        Save output to a file. If not specified print to stdout instead.

        Args:
            output: path to output file.
        """
        async with self.postgres as db_conn:
            result = await ArticleService.get_all_article_ranked(db_conn)

        result_map = map(lambda a: f"{a.score:7d} {a.url}\n", result)
        if output:
            with open(output, 'w') as f:
                f.writelines(result_map)
            logger.debug("Wrote %d output to %s", len(result), output)
        else:
            logger.debug("Logging %d output to stdout...", len(result))
            for line in result_map:
                print(line, end="")