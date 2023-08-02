import asyncio
from logging import config
from vnexpress_crawler import VnExpressCrawler
from comment_parser import CommentParser

class Pipeline:
    def __init__(self):
        self.crawler = VnExpressCrawler()
        self.parser = CommentParser()

    async def start(self):
        crawler_result = await self.crawler.start()
        parser_result = await self.parser.start(crawler_result)
        return parser_result

def config_logger(config_path):
    config.fileConfig(config_path, disable_existing_loggers=False)

async def main():
    config_logger("config/logging.ini")
    pipeline = Pipeline()
    await pipeline.start()

asyncio.run(main())
