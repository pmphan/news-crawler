"""Populate article item with scores."""
import json
import asyncio
from logging import getLogger
from aiohttp import ClientSession, DummyCookieJar
from itemadapter import ItemAdapter


logger = getLogger(f"scrapy.{__name__}")

class CommentPipeline:
    """
    Populate article item with scores. Drop item with comment count 0.
    """
    def __init__(self):
        # API to get comment details
        self.comment_api = "https://usi-saas.vnexpress.net"

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

    async def calculate_score(self, adapter):
        """
        Return score of article.
        """
        score = 0
        response = await self.get_comments(adapter)
        results = self.parse_api_response(response)
        score += results["score"]

        # Calculate score from replys to comment
        tasks = []
        for comment_id, reply_count in results["comment_replys"].items():
            if reply_count > 0:
                tasks.append(self.get_comment_replys(
                    adapter, comment_id, reply_count
                ))
        results = await asyncio.gather(*tasks)
        for result in results:
            parsed = self.parse_api_response(result)
            score += parsed["score"]
        return score

    async def get_comments(self, adapter):
        """
        Query for comment details.
        """
        params = {
            "offset": 0,
            "limit": adapter["comment_count"],
            "sort": "like",
            "objectid": adapter["article_id"],
            "objecttype": adapter["article_type"],
            "category_id": adapter["category_id"],
            "siteid": 1000000
        }
        async with self._session.get("/index/get", params=params) as response:
            logger.info("Comments GET <%d %s>", response.status, response.url)
            response.raise_for_status()
            return await response.json(content_type=None)

    async def get_comment_replys(self, adapter, comment_id, reply_count):
        """
        Query for comment reply of a particular comment.
        """
        params = {
            "offset": 0,
            "limit": reply_count,
            "sort_by": "like",
            "objectid": adapter["article_id"],
            "objecttype": adapter["article_type"],
            "id": comment_id,
            "siteid": 1000000,
        }
        async with self._session.get("/index/getreplay", params=params) as response:
            logger.info("Replys GET <%d %s>", response.status, response.url)
            response.raise_for_status()
            return await response.json(content_type=None)

    def parse_api_response(self, response):
        """
        Parse API response into dict format and calculate sum of all user likes.
        """
        items = response["data"]["items"]
        tentative_score = 0
        for item in items:
            # Early terminate because we already sorted by like count
            if item.get("userlike", 0) == 0:
                break
            tentative_score += item["userlike"]

        return {
            "score": tentative_score,
            "comment_replys": {
                # {comment_id: reply_count}
                item.get("comment_id"): item.get("replys", {}).get("total", 0) for item in items
            }
        }