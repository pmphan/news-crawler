import logging
from itertools import chain
from datetime import datetime, timedelta

import asyncio
from bs4 import BeautifulSoup

from schema.article import Article
from crawlers.crawl_session import CrawlSession

logger = logging.getLogger(__name__)

class VnExpressCrawler():

    def __init__(self, days_ago: int=7, buffer_limit=25):
        """
        Args:
            days_ago: How many day ago should the crawl start
        """
        super().__init__()
        # VnExpress allows to search articles by date range and categories, which
        # we will exploit for our crawl. The params for query are
        # {
        #   cateid = ,
        #   fromdate = ,
        #   todate = ,
        #   page = ,
        # }
        self.base_url = "https://vnexpress.net"
        self.article_query_url = "https://vnexpress.net/category/day"

        # How many article to return each crawl. This is not a hard limit.
        self.buffer_limit = buffer_limit

        # Initiate start crawl timestamp and end crawl timestamp (default to today)
        to_date = datetime.now()
        from_date = to_date - timedelta(days_ago)

        self.from_timestamp = int(from_date.timestamp())
        self.to_timestamp = int(to_date.timestamp())

    async def start(self):
        """
        Start the crawl.
        """
        # Manually added categories ID.
        # Also obtainable from https://vnexpress.net/microservice/fc
        # or https://s1cdn.vnecdn.net/vnexpress/restruct/j/v4873/v3/production/config/category.js
        categories = {
            1001005: "thoi-su",
            1003450: "goc-nhin",
            # 1001002: "the-gioi",
            # 1003159: "kinh-doanh",
            # 1005628: "bat-dong-san",
            # 1002691: "giai-tri",
            # 1002565: "the-thao",
            # 1001007: "phap-luat",
            # 1003497: "giao-duc",
            # 1003750: "suc-khoe",
            # 1002966: "doi-song",
            # 1003231: "du-lich",
            # 1001009: "khoa-hoc",
            # 1002592: "so-hoa",
            # 1001006: "xe",
            # 1001012: "y-kien",
            # 1001014: "tam-su",
            # 1001011: "cuoi",
            # 1004565: "tuyen-dau-chong-dich"       # empty category
        }

        # Aggregated list of all article in the query.
        article_master_list = []
        url_pattern = f"{self.article_query_url}?cateid=%d&fromdate=%d&todate=%d"

        # Make start URLS from categories above
        start_urls = [url_pattern % (catid, self.from_timestamp, self.to_timestamp) for catid in categories.keys()]

        async with CrawlSession() as session:
            async for article_list in self.__follow_urls__(start_urls, session):
                # Reserve space to limit buffer length of article_master_list here.
                article_master_list.extend(article_list)
                if len(article_master_list) >= self.buffer_limit:
                    yield article_master_list
                    article_master_list = []

        if article_master_list:
            yield article_master_list

    async def __follow_urls__(self, url_queue: list, session):
        """
        Follow URLs and goto next page links (if exists) one at at time down until no more next page.

        Args:
            url_queue:
                Starting urls list
            session:
                Current CrawlSession
        """
        terminate = False
        while not terminate:
            tasks = []
            for url in url_queue:
                if url is not None:
                    tasks.append(
                        # Parse article returning list of article and next page links.
                        session.create_request(
                            url, callback=self.__parse_articles_query_result__
                        )
                    )
            if not tasks:
                # Terminate loop if list of task is empty:
                terminate = True
            else:
                result = await asyncio.gather(*tasks)
                # Unzip result (of form [[article_list, url], [article_list, url],...])
                # into separate [article list, article_list,...] and [url, url,...]
                article_lists, url_queue = list(zip(*result))
                yield chain.from_iterable(article_lists)

    def __parse_articles_query_result__(self, text):
        """
        Parse result with BeautifulSoup. Return all articles.

        Args:
            text: Raw HTML text.

        Returns:
            list of articles, url to next page (None if no url)
        """
        soup = BeautifulSoup(text, 'html.parser')
        article_lists = self.__extract_articles__(soup)
        next_page_url = self.__extract_next_page__(soup)
        return (article_lists, next_page_url)

    def __extract_articles__(self, soup):
        """
        Extract and return all article info.

        Args:
            soup: The parsed version of the html.
        """
        article_lists = []
        article_blocks = soup.select("article.item-news-common")
        category_id = soup.select_one("nav.main-nav li.active").attrs["data-id"]

        for article_block in article_blocks:
            title = article_block.select_one("h3").text
            url = article_block.select_one("h3 a").attrs["href"]

            article_meta = article_block.select_one("span.txt_num_comment")
            article_id = article_meta.attrs["data-objectid"]
            article_type = article_meta.attrs["data-objecttype"]

            article_lists.append(
                Article(
                    url=url, title=title,
                    _id=article_id, _type=article_type,
                    _category_id=category_id
                )
            )
        logger.debug("Extracted %d articles.", len(article_lists))
        return article_lists
 
    def __extract_next_page__(self, soup):
        """
        Extract and return link to next page if exists.

        Args:
            soup: The parsed version of the html.
        """
        next_page_elem = soup.select_one("a.next-page[href]")

        if next_page_elem and 'disable' not in next_page_elem.attrs["class"]:
            absolute_url = next_page_elem.attrs["href"]
            return self.base_url + absolute_url
