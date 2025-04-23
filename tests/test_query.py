import json
import pathlib
from unittest import TestCase
import dataclasses
from unittest.mock import MagicMock, Mock, PropertyMock, patch

from youtube_searcher.query import QueryDict, QueryList, ResultsIterator

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

    def test_check(self):
        value = {'name': 'Kendall', 'location': {
            'america': 'NY'}, 'ages': [24, 25]}

        instance = QueryDict(value)
        result = instance.check('name', value)
        self.assertFalse(result)

        result = instance.check('location', value)
        self.assertTrue(result)

        result = instance.check('ages', value)
        self.assertFalse(result)
        self.assertIsInstance(instance.queried_data, list)

    def test_video_query_path(self):
        query_path = 'contents__twoColumnSearchResultsRenderer__primaryContents__sectionListRenderer__contents'
        instance = QueryDict(self.data)
        self.assertEqual(len(query_path.split('__')),
                         5, "Key length is not valid")
        qs1 = instance.filter(query_path)
        self.assertIsInstance(qs1, (QueryDict, QueryList))
        self.assertIsNone(qs1.queried_data)

    def test_can_get_dict(self):
        instance = QueryDict({'name': 'Kendall'})
        result = dict(instance)
        print(result)


class TestQueryList(TestCase):
    def test_simple_list(self):
        value = [
            {'name': 'Kendall'},
            {'name': 'Kylie'},
        ]

        instance = QueryList(value)
        item = instance[0]
        self.assertIsInstance(item, QueryDict)

    def test_non_dict_list(self):
        instance = QueryList([1, 2, 3])
        item = instance[0]
        qs = item.filter('text')
        print(instance.queried_data, instance.initial_data)


class TestResultIterator(TestCase):
    @classmethod
    def setUpClass(cls):
        @dataclasses.dataclass
        class SimpleModel:
            name: str

        mocked_search = MagicMock()
        mocked_search.load_cache.return_value = None
        type(mocked_search).path_to_items = PropertyMock(return_value='name')
        mocked_search.result_generator.return_value = [{'name': 'Kendall'}]
        type(mocked_search).model = PropertyMock(return_value=SimpleModel)

        instance = ResultsIterator()
        instance.response_data = {'name': 'Kendall'}
        instance.search_instance = mocked_search

        cls.instance = instance
        cls.mocked_search = mocked_search

    def test_structure(self):
        with patch.object(ResultsIterator, '__get__', spec=ResultsIterator) as mock_get:
            # result = self.instance.__get__('Instance', cls=None)
            # self.assertEqual(result, 'Instance')

            # mock_get.assert_called_once_with("some_instance", None)

            items = list(self.instance)
            print(items)
            # for item in items:
            #     with self.subTest(item=item):
            #         self.assertTrue(dataclasses.is_dataclass(item))

            # self.mocked_search.assert_called_once()
