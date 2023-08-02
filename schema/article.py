from dataclasses import dataclass, fields


@dataclass
class Article:
    url: str            # URL of article
    title: str          # Article title
    _id: int            # Article ID per VnExpress data
    _type: int          # Article type per VnExpress data
    _category_id: int   # Category article is in
    score: int = 0      # Score = sum of comment likes, default to 0

    @property
    def full_identifier(self) -> str:
        return f"{self._id}-{self._type}"