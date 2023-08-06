
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta

from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from vnexpress.items import Article
from vnexpress.helper.comment_counter import BaseCounter


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

        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_ago)

        self.from_timestamp = int(datetime.timestamp(from_date))
        self.to_timestamp = int(datetime.timestamp(to_date))

        if not getattr(self, "comment_counter", None):
            raise ValueError(f"Please define a valid CommentParser for {type(self).__name__}")

    def parse_articles(self, response):
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
            method="GET",
            callback=self.populate_comment_count,
            cb_kwargs={"articles": articles}
        )

    def populate_comment_count(self, response, articles: list[Article]):
        """
        Add comment count data to article and yield.

        Args:
            articles: list of Article objects.
        """
        comment_count_dict = self.comment_counter.parse_comment_count_response(response)
        for article in articles:
            article.comment_count = comment_count_dict[article.identifier]
            yield article

    @abstractmethod
    def get_article_list(self, response):
        return []