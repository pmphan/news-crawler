# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from abc import ABCMeta
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
