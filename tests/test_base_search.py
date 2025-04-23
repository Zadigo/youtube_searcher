import json
import pathlib
from dataclasses import dataclass, is_dataclass
from unittest import TestCase
from unittest.mock import Mock, patch

from requests import Response, Session

from youtube_searcher.search import BaseSearch

# {
#     "context": {
#         "client": {
#             "clientName": "WEB",
#             "clientVersion": "2.20210224.06.00",
#             "newVisitorCookie": false
#         },
#         "user": {
#             "lockedSafetyMode": false
#         }
#     },
#     "query": "Jalousie Princess",
#     "client": {
#         "hl": "en",
#         "gl": "US"
#     },
#     "params": "EgIQAQ%3D%3D"
# }

TEST_DIR = pathlib.Path('.').joinpath('tests').absolute()


@dataclass
class TestModel:
    itemSectionRenderer: str = None
    continuationItemRenderer: str = None


@patch.object(Session, 'send')
class TestBaseSearch(TestCase):
    @classmethod
    def setUpClass(cls):
        path = TEST_DIR.joinpath('data', 'video_search.json')
        with open(path, mode='r', encoding='utf-8') as f:
            cls.data = json.load(f)

            mock_response = Mock(spec=Response)
            mock_response.json.return_value = cls.data
            cls.mock_response = mock_response

    def test_structure(self, mock_session: Mock):
        mock_session.return_value = self.mock_response

        instance = BaseSearch('Test Value')
        instance.model = TestModel
        path_to_items = 'contents__twoColumnSearchResultsRenderer__primaryContents__sectionListRenderer__contents'
        instance.path_to_items = path_to_items

        values = list(instance.results_iterator)
        mock_session.assert_called_once()

        self.assertIsInstance(values, list)

        for value in values:
            with self.subTest(value=value):
                self.assertTrue(is_dataclass(value))

    # def test_video_search(self, mock_session: Mock):
    #     mock_session.return_value = self.mock_response

    #     instance = Videos('Some query')
    #     path_to_items = 'contents__twoColumnSearchResultsRenderer__primaryContents__sectionListRenderer__contents'
    #     instance.path_to_items = path_to_items

    #     values = list(instance.results_iterator)

    #     for value in values:
    #         with self.subTest(value=value):
    #             self.assertTrue(is_dataclass(value))

    #     item = values[0]
    #     print(item)
