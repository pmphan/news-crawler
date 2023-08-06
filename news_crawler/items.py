# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from abc import ABCMeta
from typing import Literal
from datetime import datetime
from dataclasses import dataclass


@dataclass(kw_only=True)
class BaseArticle(metaclass=ABCMeta):
    """
    Article item.
    """
    url: str                    # URL of article
    title: str                  # Article title
    comment_count: int = 0      # Number of comment on article
    score: int = 0              # Article score
    identifier: str = ""        # Identifier used by the news site

@dataclass(kw_only=True)
class VnExpressArticle(BaseArticle):
    article_id: str             # Article ID per VnExpress data
    article_type: int           # Article type per VnExpress data
    category_id: str            # Article category per VnExpress data

    def __post_init__(self):
        self.identifier = f"{self.article_id}-{self.article_type}"
        # Enforce type for article_type
        self.article_type = int(self.article_type)

@dataclass(kw_only=True)
class TuoiTreArticle(BaseArticle):
    published_time: datetime    # Published timestamp in UTC
    category: str = ""          # Category name
    item_type: Literal["article", "video"]
