import asyncio
from logging import getLogger
from .comment_scorer import BaseScorer

logger = getLogger(f"scrapy.{__name__}")
class VnExpressScorer(BaseScorer):
    comment_api = "https://usi-saas.vnexpress.net"

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
        return await self.fetch_json("/index/get", params=params)

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
        return await self.fetch_json("/index/getreplay", params=params)

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