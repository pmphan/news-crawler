import json
import asyncio
from logging import getLogger
from .comment_scorer import BaseScorer

logger = getLogger(f"scrapy.{__name__}")
class TuoiTreScorer(BaseScorer):
    comment_api = "https://id.tuoitre.vn"

    async def calculate_score(self, adapter):
        """
        Calculate score per article.
        """
        response = await self.get_comments(adapter)
        score = self.parse_api_response(response)
        return score

    async def get_comments(self, adapter):
        """
        Query for comment details.
        """
        params = {
            "objId": adapter["identifier"],
            "sort": 2,                          # Sort by most like
            "objType": 1,
            "pageSize": adapter["comment_count"]
        }
        return await self.fetch_json("/api/getlist-comment.api", params=params)

    def parse_api_response(self, response):
        """
        Parse response from get comment list API and calculate score.
        """
        # Data field is a string instead of json.
        comments = json.loads(response["Data"])
        final = 0
        for comment in comments:
            for child in comment.get("child_comments", []):
                final += child.get("likes", 0)

            # No early terminate as I wasn't exactly sure how child comment's like count
            # factor into the sort.
            likes = comment.get("likes", 0)
            final += likes
        return final