"""
VnExpress crawler.
"""
from datetime import datetime, timedelta

from scrapy import FormRequest
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from vnexpress.items import Article
from vnexpress.helper.comment_count import CommentCountParser


class VnExpressSpider(CrawlSpider):
    name = "vnexpress"
    allowed_domains = ["vnexpress.net"]

    rules = (
        Rule(
            # Rule to extract and follow next page link
            LinkExtractor(allow="/category/day", restrict_css=".next-page"),
            callback="parse_start_url", follow=True
        ),
    )

    def __init__(self, *args, days_ago: int = 30, **kwargs):
        """
        Init VnExpressSpider.

        Args:
            days_ago: Scrapy should crawl articles from how long ago.
        """
        super().__init__(*args, **kwargs)

        # Arguments passed in from command line will be parsed as string. Convert to int.
        if not isinstance(days_ago, int):
            self.logger.debug(
                "[init] days_ago = %s is of %s. Converting...", days_ago, type(days_ago)
            )
            days_ago = int(days_ago)

        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_ago)

        self.from_timestamp = int(datetime.timestamp(from_date))
        self.to_timestamp = int(datetime.timestamp(to_date))

        self.comment_parser = CommentCountParser()

        # API to get article by day
        self.by_day_api = "https://vnexpress.net/category/day"

    def start_requests(self):
        """
        VnExpress allows to search articles by date range and categories, which
        we will exploit our crawl.
        """
        # Manually added categories ID.
        categories = {
            1001005: "thoi-su",
            1003450: "goc-nhin",
            1001002: "the-gioi",
            1003159: "kinh-doanh",
            1005628: "bat-dong-san",
            1002691: "giai-tri",
            1002565: "the-thao",
            1001007: "phap-luat",
            1003497: "giao-duc",
            1003750: "suc-khoe",
            1002966: "doi-song",
            1003231: "du-lich",
            1001009: "khoa-hoc",
            1002592: "so-hoa",
            1001006: "xe",
            1001012: "y-kien",
            1001014: "tam-su",
            1001011: "cuoi",
            # 1004565: "tuyen-dau-chong-dich"       # empty category
        }
        for cat_id in categories:
            params = {
                "cateid": str(cat_id),
                "fromdate": str(self.from_timestamp),
                "todate": str(self.to_timestamp)
            }
            yield FormRequest(self.by_day_api, method="GET", formdata=params)

    def parse_start_url(self, response, **kwargs):
        """
        Get article links from search result.

        Args:
            response: Scrapy response
        """
        # Get all article on page.
        article_block_selector = "article.item-news-common"
        category_id_selector = "nav.main-nav li.active::attr(data-id)"
        category_id = response.css(category_id_selector).get()

        articles = []

        for article_block in response.css(article_block_selector):
            url = article_block.css("h3 a::attr(href)").get()
            title = article_block.css("h3 a::text").get()
            article_id = article_block.css("span.txt_num_comment::attr(data-objectid)").get()
            article_type = article_block.css("span.txt_num_comment::attr(data-objecttype)").get()
            articles.append(Article(
                url=url,
                title=title,
                article_id=article_id,
                article_type=article_type,
                category_id=category_id
            ))
            yield articles[-1]
        # comment_count_query = self.comment_parser.make_comment_count_query(articles)
        # yield FormRequest(
        #     self.comment_parser.comment_count_api,
        #     method="GET",
        #     formdata={"cid": comment_count_query},
        #     callback=self.parse_articles,
        #     cb_kwargs={"articles": articles}
        # )

    def parse_articles(self, response, articles: list[Article]):
        """
        Add comment count data to article and yield.

        Args:
            articles: list of Article objects.
        """
        comment_count_dict = self.comment_parser.parse_comment_count_response(response)
        for article in articles:
            article.comment_count = comment_count_dict[article.full_identifier]
            yield article
