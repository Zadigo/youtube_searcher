import dataclasses
import json
import pathlib
from dataclasses import dataclass, is_dataclass
from unittest import TestCase
from unittest.mock import Mock, patch

from requests import Response, Session

from youtube_searcher.search import BaseSearch, ChannelVideos, Videos

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
    # Since we have to renderer on the base
    # search model, we will get dicts
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


class SearchMixin:
    def setUp(self):
        mock_response = Mock(spec=Response)
        mock_response.json.return_value = self.data
        self.mock_response = mock_response


@patch.object(Session, 'send')
class TestSearchVideos(SearchMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        path = TEST_DIR.joinpath('data', 'video_search.json')
        with open(path, mode='r', encoding='utf-8') as f:
            cls.data = json.load(f)

    def test_search_videos(self, mock_session: Mock):
        mock_session.return_value = self.mock_response

        instance = Videos('Search video')
        path_to_items = 'contents__twoColumnSearchResultsRenderer__primaryContents__sectionListRenderer__contents'
        instance.path_to_items = path_to_items

        values = instance.objects.all()

        for value in values:
            with self.subTest(value=value):
                self.assertTrue(is_dataclass(value))

        video = values[0]
        for value in video.thumbnails:
            self.assertTrue(dataclasses.is_dataclass(value))

        self.assertTrue(dataclasses.is_dataclass(video.channel))


@patch.object(Session, 'send')
class TestSearchChannel(SearchMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        path = TEST_DIR.joinpath('data', 'channel_search.json')
        with open(path, mode='r', encoding='utf-8') as f:
            cls.data = json.load(f)

    def test_channel_search_videos(self, mock_session: Mock):
        mock_session.return_value = self.mock_response

        instance = ChannelVideos('Search video', 'some_id')
        values = instance.objects.all()

        for value in values:
            with self.subTest(value=value):
                self.assertTrue(is_dataclass(value))

        print(values)
        # item = values[0]
        # print(item)
