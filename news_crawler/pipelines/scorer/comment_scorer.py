"""Populate article item with scores."""
import asyncio
from abc import ABC, abstractmethod
from logging import getLogger
from aiohttp import ClientSession, DummyCookieJar
from itemadapter import ItemAdapter


logger = getLogger(f"scrapy.{__name__}")

class BaseScorer(ABC):
    """
    Populate article item with scores. Drop item with comment count 0.
    """
    # API to get comment details
    comment_api: str
    def __init__(self):
        if not getattr(self, "comment_api", None):
            raise ValueError(f"Please define the comment API for {type(self).__name__}")

    def open_spider(self, spider):
        # Start asyncio session
        self._session = ClientSession(base_url=self.comment_api, cookie_jar=DummyCookieJar())

    def close_spider(self, spider):
        loop = asyncio.get_event_loop()
        asyncio.create_task(self.dispose_client())

    async def dispose_client(self):
        logger.debug("Comment Async session closed.")
        await self._session.close()

    async def process_item(self, item, spider):
        """
        Process article. Drop item with comment count 0.
        """
        adapter = ItemAdapter(item)
        if adapter["comment_count"] <= 0:
            logger.debug(
                "Article %s (%s) has 0 comment. Auto-skipped.",
                adapter["identifier"], adapter["title"]
            )
            return item

        score = await self.calculate_score(adapter)
        adapter["score"] = score
        logger.debug(
            "Article %s set score to %d (%s)",
            adapter["identifier"], adapter["score"], adapter["title"]
        )
        return item

    async def fetch_json(self, endpoint, params):
        async with self._session.get(endpoint, params=params) as response:
            logger.info("%s GET <%d %s>", self.__class__.__name__, response.status, response.url)
            response.raise_for_status()
            return await response.json(content_type=None)

    @abstractmethod
    async def calculate_score(self, adapter) -> int:
        """Return score of article."""
        return 0