
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta, timezone

from scrapy import Request
from scrapy.spiders import CrawlSpider

from news_crawler.helper.comment_counter import BaseCounter


class BaseCrawler(CrawlSpider, metaclass=ABCMeta):
    comment_counter: BaseCounter

    def __init__(self, *args, days_ago: int = 30, **kwargs):
        """
        Init BaseCrawler.

        Args:
            days_ago: Scrapy should crawl articles from how long ago.
        """
        super().__init__(*args, **kwargs)

        # Arguments passed in from command line will be parsed as string. Convert to int.
        if not isinstance(days_ago, int):
            self.logger.debug(
                "[init][%s] days_ago = %s is of %s. Converting...", self.name, days_ago, type(days_ago)
            )
            days_ago = int(days_ago)

        self.to_datetime = datetime.now(timezone.utc)
        self.from_datetime = self.to_datetime - timedelta(days=days_ago)

        self.logger.debug(
            "Crawling from %s to %s",
            self.from_datetime.strftime("%b %d"),
            self.to_datetime.strftime("%b %d")
        )

        if not getattr(self, "comment_counter", None):
            raise ValueError(f"Please define a valid CommentParser for {type(self).__name__}")

    def parse_start_url(self, response, **kwargs):
        """
        Get list of article links from search result.

        Args:
            response: Scrapy response
        """
        # Get all article on page.
        articles = self.get_article_list(response)

        # Query for comment count and populate Article object with it.
        yield Request(
            self.comment_counter.make_comment_count_url(articles),
            dont_filter=True,
            method="GET",
            callback=self.populate_comment_count,
            cb_kwargs={"articles": articles}
        )

    def populate_comment_count(self, response, articles: list):
        """
        Add comment count data to article and yield.

        Args:
            articles: list of Article objects.
        """
        comment_count_dict = self.comment_counter.parse_comment_count_response(response)
        for article in articles:
            article.comment_count = comment_count_dict[article.identifier]
            yield article
        return article

    @abstractmethod
    def get_article_list(self, response):
        return []