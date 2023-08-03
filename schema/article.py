from dataclasses import dataclass, fields, asdict


@dataclass
class Article:
    """
    Schema for parsing article.
    Might switch to pydantic if performance is good.
    """
    url: str            # URL of article
    title: str          # Article title
    article_id: str     # Article ID per VnExpress data
    article_type: int   # Article type per VnExpress data
    category_id: str    # Category article is in
    score: int = 0      # Score = sum of comment likes, default to 0

    def __post_init__(self):
        # Enforce article type as int:
        self.article_type = int(self.article_type)

    def full_identifier(self) -> str:
        return f"{self.article_id}-{self.article_type}"

    def dict(self):
        return self.__dict__.copy()