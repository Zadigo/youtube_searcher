import json
from typing import Generic, Iterator, Optional
from urllib.parse import urlencode

from requests import Request, Session

from youtube_searcher.constants import SEARCH_KEY, USER_AGENT, SearchModes
from youtube_searcher.models.videos import VideoModel
from youtube_searcher.query import Query, QueryDict, ResultsIterator
from youtube_searcher.typings import DC, QL, D, Q


class BaseSearch(Generic[Q, QL, DC]):
    model: DC = None
    objects = ResultsIterator()

    def __init__(self, query: str, limit: Optional[int] = 10, language: Optional[str] = 'en', region: Optional[str] = 'US', search_preferences: Optional[str] = None, timeout: Optional[int] = None):
        self.query = query
        self.limit = limit
        self.language = language
        self.region = region
        self.search_preferences = search_preferences
        self.timeout = timeout
        self.continuation_key = None
        self.estimate_results: Optional[int] = None
        # The path to the list of items that
        # we are interested in a__b__c
        self.path_to_items: Optional[str] = None

    def result_generator(self, queryset: QL) -> Iterator[D]:
        """Custom method used to generate the final results
        of a target element within the response data. The target
        value should return a list of dictionnaries containing 
        the key, value pairs that should be kept"""
        if isinstance(queryset, QueryDict):
            raise ValueError(
                "Result generator requires a "
                "QueryList of items to iterate"
            )

        # if isinstance(queryset, list):
        #     queryset = QueryList(queryset)

        for item in queryset:
            yield item

    def get_url(self, **query: str):
        encoded_key = urlencode({'key': SEARCH_KEY, **query})
        return f'https://www.youtube.com/youtubei/v1/search?{encoded_key}'

    def get_payload(self, **extra: str):
        """Needs to be implemented by the subclasses in order
        to create the payload that will be used with the request"""
        base_payload = {
            'context': {
                'client': {
                    'clientName': 'WEB',
                    'clientVersion': '2.20210224.06.00',
                    'newVisitorCookie': True
                },
                'user': {
                    'lockedSafetyMode': False
                }
            }
        }
        return base_payload | extra

    def create_request(self, exta_payload: dict[str, str] = {}, url_query: dict[str, str] = {}):
        session = Session()

        payload = self.get_payload(**exta_payload)
        data = json.dumps(payload).encode('utf-8')

        params = {
            'method': 'post',
            'url': self.get_url(**url_query),
            'data': data
        }

        request = Request(**params)
        prepared_request = session.prepare_request(request)

        prepared_request.headers.update(**{
            'Content-Type': 'application/json; charset=utf-8',
            'User-Agent': USER_AGENT,
            'Content-Length': len(data)
        })

        return session, prepared_request


class Search(BaseSearch):
    def __init__(self, query: str, *, limit: int = 20, **kwargs: str | int):
        super().__init__(query, limit, **kwargs)


class Videos(BaseSearch):
    """Search videos on YouTube"""

    model = VideoModel

    def __init__(self, query: str, *, limit: int = 20, **kwargs: str):
        super().__init__(query, limit, search_preferences=SearchModes.videos, **kwargs)
        self.path_to_items = 'contents__twoColumnSearchResultsRenderer__primaryContents__sectionListRenderer__contents'

    def result_generator(self, queryset: Query) -> Iterator[D]:
        for item in queryset:
            if 'itemSectionRenderer' in item:
                for content in item['itemSectionRenderer']['contents']:
                    value = content.get('videoRenderer', None)
                    if value is None:
                        continue

                    yield {
                        'video_id': value['videoId'],
                        'thumbnails': value['thumbnail']['thumbnails'],
                        'title': value['title']['runs'][-1]['text'],
                        'publication_text': value['publishedTimeText']['simpleText'],
                        'duration': value['lengthText']['simpleText'],
                        'view_count_text': value['viewCountText']['simpleText'],
                        'search_key': value['searchVideoResultEntityKey'],
                        'channel': value['ownerText']['runs']
                    }
            elif 'continuationItemRenderer' in item:
                continue

    def get_payload(self, **extra: dict[str, str]):
        payload = super().get_payload(**extra)

        payload['query'] = self.query
        payload['client'] = {
            'hl': self.language,
            'gl': self.region
        }

        if self.search_preferences:
            payload['params'] = self.search_preferences

        if self.continuation_key is not None:
            payload['continuation'] = self.continuation_key
        return payload


class Channels(BaseSearch):
    pass


class Playlists(BaseSearch):
    pass


class ChannelVideos(BaseSearch):
    pass


class Custom(BaseSearch):
    pass
