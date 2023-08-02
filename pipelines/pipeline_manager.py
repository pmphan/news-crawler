from crawlers.vnexpress_crawler import VnExpressCrawler
from parsers.comment_parser import CommentParser
from database.postgres import Postgres
from schema.postgres import Base
from database.article_service import ArticleService

class PipelineManager:
    async def init_services(self, config):
        """
        Init all needed services.
        """
        self.init_db(self, config)

        self.parser = CommentParser()

        if "crawler" in config:
            logger.info("[crawler] Initing VnExpress crawler.")
            crawler_config = config["crawlers"]
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

    async def init_db(self):
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
        else:
            for line in result_map:
                print(line)