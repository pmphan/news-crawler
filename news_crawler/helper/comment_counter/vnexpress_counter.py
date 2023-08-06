import re
from functools import reduce
from .base_counter import BaseCounter

class VnExpressCounter(BaseCounter):
    """
    Helper class to parse comment from VnExpress.
    """
    comment_count_api = "https://usi-saas.vnexpress.net/widget/index/"

    def make_comment_count_url(self, article_list):
        """
        Make comment count query from article list. Query is of the form:
        https://usi-saas.vnexpress.net/widget/index/?cid=id-type;id-type;id-type;

        Args:
            article: List of Article objects.

        Returns:
            str: valid query url matching form above
        """
        query = reduce(lambda ac, article: f"{ac};{article.identifier}", article_list, "")
        return f"{self.comment_count_api}?cid={query}"

    def parse_comment_count_response(self, response) -> str:
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
