"""
VnExpress crawler.
"""
from scrapy import FormRequest
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor

from .crawler import BaseCrawler
from news_crawler.items import VnExpressArticle
from news_crawler.helper.comment_counter import VnExpressCounter


class VnExpressSpider(BaseCrawler):
    name = "vnexpress"
    allowed_domains = ["vnexpress.net"]
    comment_counter = VnExpressCounter()

    rules = (
        Rule(
            # Rule to extract and follow next page link
            LinkExtractor(allow="/category/day", restrict_css=".next-page"),
            callback="parse_start_url", follow=True
        ),
    )

    def __init__(self, *args, days_ago: int = 30, **kwargs):
        super().__init__(*args, days_ago=days_ago, **kwargs)
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

    def get_article_list(self, response):
        """
        Get list of articles from response.

        Return:
            list of Article objects.
        """
        article_block_selector = "article.item-news-common"
        category_id_selector = "nav.main-nav li.active::attr(data-id)"
        category_id = response.css(category_id_selector).get()

        articles = []

        for article_block in response.css(article_block_selector):
            url = article_block.css("h3 a::attr(href)").get()
            title = article_block.css("h3 a::text").get()
            article_id = article_block.css("span.txt_num_comment::attr(data-objectid)").get()
            article_type = article_block.css("span.txt_num_comment::attr(data-objecttype)").get()
            articles.append(VnExpressArticle(
                url=url,
                title=title,
                article_id=article_id,
                article_type=article_type,
                category_id=category_id
            ))
        return articles