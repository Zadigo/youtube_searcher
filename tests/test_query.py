import dataclasses
import json
import pathlib
from unittest import TestCase
from unittest.mock import MagicMock, Mock, PropertyMock, patch

from youtube_searcher.query import Query, QueryDict, QueryList, ResultsIterator

TEST_DIR = pathlib.Path('.').joinpath('tests').absolute()


class TestQueryDict(TestCase):
    @classmethod
    def setUpClass(cls):
        path = TEST_DIR.joinpath('data', 'video_search.json')
        with open(path, mode='r', encoding='utf-8') as f:
            cls.data = json.load(f)

        cls.simple_data = {
            'text': {
                'name': 'Julie',
                'age': {
                    'europe': 19,
                    'america': 25
                }
            }
        }

    def test_simple_dict(self):
        instance = QueryDict(self.simple_data)

        expected = {'name': 'Julie', 'age': {'europe': 19, 'america': 25}}
        # Test: Item is dictionnary
        qs = instance.filter('text')
        self.assertDictEqual(qs.cache, expected)

    def test_chaining(self):
        instance = QueryDict(self.simple_data)

        qs1 = instance.filter('text')
        qs2 = qs1.filter('age__europe')
        self.assertDictEqual(qs2.cache, self.simple_data['text']['age'])

    def test_get(self):
        instance = QueryDict({'age': 15, 'location': {'country': 'Europe'}})
        self.assertEqual(instance.get('age'), 15)
        self.assertEqual(instance.get('location__country'), 'Europe')

    def test_check(self):
        value = {
            'name': 'Kendall',
            'ages': [24, 25],
            'location': {
                'america': 'NY'
            }
        }

        instance = QueryDict(value)
        result, _ = instance.check('name', value)
        self.assertFalse(result)

        result, _ = instance.check('location', value)
        self.assertTrue(result)

        result, _ = instance.check('ages', value)
        self.assertFalse(result)


class TestQueryList(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.values = [
            {'name': 'Kendall', 'location': {'country': 'USA', 'city': None}},
            {'name': 'Kylie', 'location': {'country': 'USA', 'city': None}},
        ]

    def test_simple_list(self):

        instance = QueryList(self.values)
        item = instance[0]
        self.assertIsInstance(item, QueryDict)

    def test_non_dict_list(self):
        instance = QueryList([1, 2, 3])
        item = instance[0]
        qs = item.filter('text')
        print(qs)

    def test_filter_dicts(self):
        instance = QueryList(self.values)
        result = instance.filter('location__country')

        expected = self.values[0]['location']
        for item in result:
            with self.subTest(item=item):
                self.assertDictEqual(item.cache, expected)


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
