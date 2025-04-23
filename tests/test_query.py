import json
import pathlib
from unittest import TestCase
from unittest.mock import Mock, patch

from youtube_searcher.query import QueryDict, QueryList

TEST_DIR = pathlib.Path('.').joinpath('tests').absolute()


class TestQueryDict(TestCase):
    @classmethod
    def setUpClass(cls):
        path = TEST_DIR.joinpath('data', 'video_search.json')
        with open(path, mode='r', encoding='utf-8') as f:
            cls.data = json.load(f)

    def test_simple_dict(self):
        data = {'text': {'name': 'Julie', 'age': {'europe': 19, 'america': 25}}}
        instance = QueryDict(data)

        expected = {'name': 'Julie', 'age': {'europe': 19, 'america': 25}}
        # Test: Item is dictionnary
        qs = instance.filter('text')
        self.assertDictEqual(qs.queried_data, expected)

        # This should return the dict in which
        # the value should be not the value itself ??
        # or should we return the value ??
        qs2 = instance.filter('name')
        self.assertDictEqual(qs2.queried_data, expected)

        expected = {'europe': 19, 'america': 25}
        qs3 = instance.filter('age__europe')
        self.assertDictEqual(qs3.queried_data, expected)

    def test_video_query_path(self):
        query_path = 'contents__twoColumnSearchResultsRenderer__primaryContents__sectionListRenderer__contents'
        instance = QueryDict(self.data)
        self.assertEqual(len(query_path.split('__')),
                         5, "Key length is not valid")
        qs1 = instance.filter(query_path)
        self.assertIsInstance(qs1, (QueryDict, QueryList))
        self.assertIsNone(qs1.queried_data)


class TestQueryList(TestCase):
    def test_simple_list(self):
        value = [
            {'name': 'Kendall'},
            {'name': 'Kylie'},
        ]

        instance = QueryList(value)
        item = instance[0]
        self.assertIsInstance(item, QueryDict)
