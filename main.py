import asyncio
from logging import config, getLogger
from configparser import ConfigParser
from pipelines.pipeline_manager import PipelineManager
from database.article_service import ArticleService

from argparse import ArgumentParser

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
    pipeline = PipelineManager()
    await pipeline.init_services(sv_config)
    await pipeline.start()

async def get_result():
    config_logger("config/logging.ini")
    sv_config = config_services("config/service.ini")
    pipeline = PipelineManager()
    await pipeline.init_services(sv_config)

    # Get output path
    output = None
    if sv_config["output"]:
        output = sv_config["output"]["name"]
    await pipeline.get_ranked_result(output)

async def main():
    parser = ArgumentParser(prog="run_crawl", description="Run crawler.")
    parser.add_argument("-r", "--result", help="Flag to only read result from DB instead of running crawl.", action="store_true")
    args = parser.parse_args()
    if args.result:
        await get_result()
    else:
        await run_crawler()
        await get_result()

if __name__ == "__main__":
    asyncio.run(main())