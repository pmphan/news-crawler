from dataclasses import dataclass


@dataclass
class Article:
    url: str            # URL of article
    title: str          # Article title
    _id: int            # Article ID per VnExpress data
    _type: int          # Article type per VnExpress data