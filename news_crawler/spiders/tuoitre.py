from datetime import datetime
from scrapy import Request

from .crawler import BaseCrawler
from news_crawler.items import TuoiTreArticle
from news_crawler.helper.comment_counter import TuoiTreCounter

class TuoiTreSpider(BaseCrawler):
    name = "tuoitre"
    allowed_domains = ["tuoitre.vn"]
    comment_counter = TuoiTreCounter()
    start_urls = [
        "https://tuoitre.vn/timeline/0/trang-1.htm",
        "https://tuoitre.vn/timeline/search.htm?pageindex=1"
    ]

    def __init__(self, *args, days_ago: int = 30, **kwargs):
        super().__init__(*args, days_ago=days_ago, **kwargs)
        self.article_index = 1
        self.video_index = 1

    @property
    def article_url(self):
        return f"https://tuoitre.vn/timeline/0/trang-{self.article_index}.htm"

    @property
    def video_url(self):
        return f"https://tuoitre.vn/timeline/search.htm?pageindex={self.video_index}"

    def start_requests(self):
        yield Request(url=self.article_url)
        yield Request(url=self.video_url)

    def parse_start_url(self, response, **kwargs):
        yield from self.parse_articles(response)

    def get_article_list(self, response):
        article_block_selector = ".box-category-item"
        articles = []

        item_type = "video"
        if response.url.endswith(".htm"):
            item_type = "article"

        for article_block in response.css(article_block_selector):
            link_title = article_block.css(".box-category-link-title")
            url = link_title.attrib["href"]
            title = link_title.attrib["title"]
            identifier = link_title.attrib["data-id"]
            category = article_block.css(".box-category-category::text").get()

            # Published time format and selector for videos
            published_time_selector = "span.time::text"
            published_time_format = "%d/%m/%Y%z"
            if item_type == "article":
                # Published time selector and format for articles
                published_time_selector = ".time-ago-last-news::attr(title)"
                published_time_format = "%Y-%m-%dT%H:%M:%S%z"
            published_time = article_block.css(published_time_selector).get()
            # Convert published time from string GMT+7 to UTC timestamp
            published_time = datetime.strptime(published_time+"+0700", published_time_format).timestamp()
            articles.append(TuoiTreArticle(
                url=url,
                title=title,
                identifier=identifier,
                category=category,
                item_type=item_type,
                published_time=published_time
            ))
        return articles