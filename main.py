import asyncio
from logging import config, getLogger
from configparser import ConfigParser
from pipelines.pipeline_manager import PipelineManager
from database.article_service import ArticleService

logger = getLogger(__name__)

def config_logger(config_path):
    config.fileConfig(config_path, disable_existing_loggers=False)

def config_services(config_path):
    cparser = ConfigParser()
    cparser.read(config_path)
    return cparser

async def run_crawler():
    config_logger("config/logging.ini")
    sv_config = config_services("config/service.ini")
    pipeline = PipelineManager(sv_config)
    await pipeline.init_db()
    await pipeline.start()
    await pipeline.get_ranked_result('./output.txt')

if __name__ == "__main__":
    asyncio.run(run_crawler())