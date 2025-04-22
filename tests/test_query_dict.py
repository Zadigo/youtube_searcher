import json
from unittest import TestCase
from unittest.mock import Mock, patch

from tests import TEST_DIR
from youtube_searcher.search import QueryDict


class TestQueryDict(TestCase):
    @classmethod
    def setUpClass(cls):
        path = TEST_DIR.joinpath('data', 'video_search.json')
        with open(path, mode='r', encoding='utf-8') as f:
            cls.data = json.load(f)

    def test_video_query_path(self):
        query_path = 'contents__twoColumnSearchResultsRenderer__primaryContents___richGridRenderer__contents'
        instance = QueryDict(self.data, query_path)
