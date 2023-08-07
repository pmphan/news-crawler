"""
Base class for comment count parser.
"""

from abc import ABC, abstractmethod

class BaseCounter(ABC):
    """
    Helper class to parse comment.
    """
    comment_count_api: str

    def __init__(self):
        """
        Initiate vnexpress comment api helper class.
        """
        if not getattr(self, "comment_count_api", None):
            raise ValueError(f"Please define API point for {type(self).__name__}")

    @abstractmethod
    def make_comment_count_url(self, article_list) -> str:
        """
        Make comment count query from article list. Query is of the form:
        """
        return ""

    @abstractmethod
    def parse_comment_count_response(self, response) -> dict:
        """
        Return:
            dict: {identifier: comment_count}
        """
        return {}
