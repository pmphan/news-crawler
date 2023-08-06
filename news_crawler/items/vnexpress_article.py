from .base_article import BaseArticle
from dataclasses import dataclass

@dataclass(kw_only=True)
class VnExpressArticle(BaseArticle):
    article_id: str             # Article ID per VnExpress data
    article_type: int           # Article type per VnExpress data
    category_id: str            # Article category per VnExpress data

    def __post_init__(self):
        self.identifier = f"{self.article_id}-{self.article_type}"
        # Enforce type for article_type
        self.article_type = int(self.article_type)