# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass


@dataclass
class Article:
    """
    Article item.
    """
    url: str                    # URL of article
    title: str                  # Article title
    article_id: str             # Article ID per VnExpress data
    article_type: int           # Article type per VnExpress data
    category_id: str            # Article category per VnExpress data
    comment_count: int = 0      # Number of comment on article
    score: int = 0              # Article score
    identifier: str = ""   # article_id-article_type

    def __post_init__(self):
        self.identifier = f"{self.article_id}-{self.article_type}"
        # Enforce type for article_type
        self.article_type = int(self.article_type)