import asyncio
from logging import config
from configparser import ConfigParser
from pipelines.pipeline_manager import PipelineManager

def config_logger(config_path):
    config.fileConfig(config_path, disable_existing_loggers=False)

def config_endpoints(config_path):
    cparser = ConfigParser()
    cparser.read(config_path)
    return cparser

async def run_crawler():
    config_logger("config/logging.ini")
    ep_config = config_endpoints("config/endpoints.ini")
    pipeline = PipelineManager(ep_config)
    await pipeline.init_db()
    await pipeline.start()

if __name__ == "__main__":
    asyncio.run(run_crawler())