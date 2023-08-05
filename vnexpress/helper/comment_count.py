"""
Holds comment count parser.
"""

import re
from functools import reduce

class CommentCountParser:
    """
    Helper class to parse comment.
    """

    def __init__(self):
        """
        Initiate vnexpress comment api helper class.
        """
        # API to get comment count
        self.comment_count_api = "https://usi-saas.vnexpress.net/widget/index/"

    def parse_comment_count_response(self, response):
        """
        Comment count api gives response in format:
        CmtWidget.parse('widget-comment-%full-identifier%', %comment-count%);...
        Return in readable format

        Args:
            response: Response in the format above.

        Return:
            dict: {full-identifier: comment_count}
        """
        str_resp = response.text
        comment_counts = map(int, re.findall(r"(?<=\s)(\d+)", str_resp))
        # Because we can't be sure about the order of returned result,
        # we will also store the corresponding full-identifier
        full_ids = re.findall(r"(?<=comment-)(\d+-\d+)", str_resp)
        return dict(zip(full_ids, comment_counts))

    def make_comment_count_query(self, article_list):
        """
        Make comment count query from article list. Query is of the form:
        https://usi-saas.vnexpress.net/widget/index/?cid=id-type;id-type;id-type;

        Args:
            article: List of Article objects.

        Returns:
            str: id-type;id-type;id-type;
        """
        return reduce(lambda ac, article: f"{ac};{article.full_identifier}", article_list, "")
