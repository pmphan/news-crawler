from functools import reduce
from .base_counter import BaseCounter

class TuoiTreCounter(BaseCounter):
    """
    Helper class to parse comment count response from tuoitre.vn.
    """
    comment_count_api = "https://id.tuoitre.vn/api/getcount-comment.api"

    def make_comment_count_url(self, article_list):
        """
        Make comment count query from article list. Query is of the form:
        "https://id.tuoitre.vn/api/getcount-comment.api?ids=id,id,id,id"        

        Args:
            article: List of Article objects.
        """
        aids = reduce(lambda ac, article: f"{ac},{article.identifier}", article_list, "")
        return f"{self.comment_count_api}?ids={aids}"

    def parse_comment_count_response(self, response):
        """
        Comment count api gives response in format:
        {"Success": true|false, "Data":[{comment_count:0,total_count:0,object_id:id},{}]}
        Return in readable format

        Args:
            response: Response in the format above.

        Return:
            dict: {identifier: comment_count}
        """
        json_resp = response.json().get("Data", [])
        return {item["object_id"]:item["total_count"] or 0 for item in json_resp}