import re
import json
import asyncio
from logging import getLogger

from crawlers.crawl_session import CrawlSession
from schema.article import Article

logger = getLogger(__name__)

class CommentParser:
    def __init__(self):
        # VnExpress exposed a comment API with this base URL
        self.base_url = "https://usi-saas.vnexpress.net"
        # API to get comment count
        self.comment_count_api = f"{self.base_url}/widget/index/"
        # API to get comment details
        self.comment_detail_api = f"{self.base_url}/index/get"
        # API to get comment reply
        self.comment_reply_api = f"{self.base_url}/index/getreplay"

    async def start(self, article_list: list[Article]):
        """
        Start parse comment pipeline from given article list (list[Article])
        """
        async with CrawlSession() as session:
            comment_count_dict = await self.__get_comment_count__(article_list, session)
            return await self.__get_comment_details__(article_list, comment_count_dict, session)

    async def __get_comment_count__(self, article_list: list[Article], session):
        """
        Query for all article comment counts. Allow for early process if comment count is 0.

        Args:
            article_list: List of Article objects.
            session: Current session.
        """
        query = ";".join(map(lambda article: article.full_identifier(), article_list))

        response = await session.create_request(
            url=self.comment_count_api,
            params={"cid": query},
            callback=self.__parse_comment_count_response__
        )
        if len(response) != len(article_list):
            logger.error("[parser] Comment count API response length %d mismatched with article list length: %d", len(response), len(article_list))
        else:
            logger.debug("[parser] Comment count API response length %d matched article list length %d", len(response), len(article_list))
        return response

    async def __get_comment_details__(self, article_list: list[Article], comment_count_dict: dict, session):
        """
        Query for all article comment details and calculate their score. Skip article with only 0 comment.

        Args:
            article_list: List of Article objects.
            session: Current session.
        """
        logger.debug("[parser] Comment parser started parsing %d articles.", len(article_list))

        # Query for first level comments
        # ------------------------------
        tasks = []
        # Hold article that actually got queried
        queried_article_list = []
        for article in article_list:
            comment_count = comment_count_dict[article.full_identifier()]
            if comment_count == 0:
                logger.debug("[parser] Article %s (%s) comment count is %d. Auto set score to 0.", article.full_identifier(), article.title, comment_count)
            else:
                # Query for comment details
                params = {
                        "offset": 0,
                        "limit": comment_count,
                        "sort": "like",
                        "objectid": article.article_id,
                        "objecttype": article.article_type,
                        "category_id": article.category_id,
                        "siteid": 1000000
                }
                tasks.append(session.create_request(
                    self.comment_detail_api,
                    params=params,
                    callback=self.__parse_comment_details_response__,
                ))
                queried_article_list.append(article)

        # Result is of form [[score, reply_dict], [score, reply_dict],...]
        results = await asyncio.gather(*tasks)

        # Query for reply comments
        # ------------------------
        tasks = []
        queried_article_list_2 = []
        for article, (first_level_score, reply_dict) in zip(queried_article_list, results):
            # Also add first level score to article while looping
            article.score += first_level_score

            for comment_id, reply_count in reply_dict.items():
                if reply_count == 0:
                    continue

                params = {
                    "siteid": 1000000,
                    "objectid": article.article_id,
                    "objecttype": article.article_type,
                    "id": comment_id,
                    "offset": 0,
                    "limit": reply_count,
                    "sort_by": "like"
                }
                tasks.append(session.create_request(
                    self.comment_reply_api,
                    params=params,
                    callback=self.__parse_comment_score__
                ))
                queried_article_list_2.append(article)

        second_level_scores = await asyncio.gather(*tasks)

        # Add second level score to article
        for article, score in zip(queried_article_list_2, second_level_scores):
            article.score += score

        # Final log
        for article in article_list:
            logger.debug("[parser] Article %s score set to %d (%s)", article.full_identifier(), article.score, article.title)
        return article_list

    def __parse_comment_count_response__(self, response: bytes):
        """
        Comment count api gives response in format:
        CmtWidget.parse('widget-comment-%full-identifier%', %comment-count%);CmtWidget.parse('widget-comment-%full-identifier%',  %comment-count%);...

        Args:
            response: Response in the format above.
        """
        str_resp = response.decode("utf-8")
        comment_counts = map(int, re.findall(r"(?<=\s)(\d+)", str_resp))
        # Because we can't be sure about the order of returned result, we will also store the corresponding full-identifier
        full_ids = re.findall(r"(?<=comment-)(\d+-\d+)", str_resp)
        return dict(zip(full_ids, comment_counts))

    def __parse_comment_details_response__(self, response):
        """
        Args:
            article: Article item that is being parsed.
        Returns:
            - Score by summing all response
            - Reply dict in the form of {comment_id: reply_count}
        """
        str_resp = response.decode("utf-8")
        json_resp = json.loads(str_resp)
        score = self.__parse_comment_score__(json_resp)

        items = json_resp["data"]["items"]
        reply_dict = {item.get("comment_id"): item.get("replys").get("total", 0) for item in items}
        return score, reply_dict

    def __parse_comment_score__(self, resp):
        """
        Returns score by summing all response. Applicaple for response gotten from reply API.
        Modify article score in-place if article item is supplied.
        """
        if type(resp) == bytes:
            resp = resp.decode("utf-8")
            resp = json.loads(resp)

        items = resp["data"]["items"]
        tentative_score = 0
        for item in items:
            # Early terminate because we already sorted by like count
            if item["userlike"] == 0:
                break
            tentative_score += item["userlike"]

        return tentative_score
