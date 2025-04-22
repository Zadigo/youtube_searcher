import json
import pathlib
from unittest import TestCase
from unittest.mock import Mock, patch

from youtube_searcher.search import QueryDict

TEST_DIR = pathlib.Path('.').joinpath('tests').absolute()


class TestQueryDict(TestCase):
    @classmethod
    def setUpClass(cls):
        path = TEST_DIR.joinpath('data', 'video_search.json')
        with open(path, mode='r', encoding='utf-8') as f:
            cls.data = json.load(f)

    def test_video_query_path(self):
        query_path = 'contents__twoColumnSearchResultsRenderer__primaryContents__sectionListRenderer__contents'
        instance = QueryDict(self.data)
        self.assertEqual(len(query_path.split('__')),
                         5, "Key length is not valid")
        qs1 = instance.filter(query_path)
        self.assertIsInstance(qs1, QueryDict)
        self.assertIsNotNone(qs1.queried_data)

        with open('testing.json', mode='w') as f:
            json.dump(instance.queried_data, f)
