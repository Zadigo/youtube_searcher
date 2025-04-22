import asyncio
import json
from functools import cached_property, lru_cache
from typing import (AsyncIterator, Dict, Generic, Iterator, Mapping, Optional,
                    Type, TypeVar, Union)
from urllib.parse import urlencode
import itertools
from asgiref.sync import async_to_sync, iscoroutinefunction
from requests import Request, Session

from youtube_searcher.constants import SEARCH_KEY, USER_AGENT, SearchModes

B = TypeVar('B', bound='BaseSearch')

NestedJson = Union[str, int, bool, Dict[str, 'D']]
D = Mapping[str, NestedJson]

Q = TypeVar('Q', bound='Query')


class Query:
    def __init__(self, data: NestedJson):
        self.initial_data: NestedJson = data
        self.queried_data: Optional[list[D]] = None


class QueryDict(Query):
    """A helper class used to query the complex
    dicts returned by the response"""

    def __repr__(self):
        return f'<QueryDict[{self.queried_data}]>'

    def filter(self, query_path: str):
        self.keys = query_path.split('__')
        for key in self.keys:
            if self.queried_data is None:
                is_valid = self.check(key, self.initial_data)
                if is_valid:
                    self.queried_data = self.initial_data[key]
            else:
                is_valid = self.check(key, self.queried_data)
                if is_valid:
                    self.queried_data = self.queried_data[key]

        if isinstance(self.queried_data, list):
            return QueryList(self.queried_data)
        else:
            query = QueryDict(self.queried_data)
            query.queried_data = self.queried_data
            return query

    def check(self, key: str, data: D):
        """A function that indicates wether the item is a
        dictionnary and therefore abled to be keyed"""
        value = data[key]
        if isinstance(value, str):
            return False
        elif isinstance(value, int):
            return False
        elif isinstance(value, dict):
            return True
        elif isinstance(value, list):
            # If the vvalue is a group of
            # values, just set them directly
            # on property
            self.queried_data = value
        else:
            return False


class QueryList(Query):
    def __init__(self, initial_data: list):
        super().__init__(initial_data)

    def __iter__(self):
        for item in self.initial_data:
            yield item


class ResultsIterator(Generic[B]):
    def __init__(self):
        self.search_instance: B | None = None
        self.response_data: dict[str, str] | None = None

    def __get__(self, instance: B, cls: Optional[Type[B]] = None):
        self.search_instance = instance
        return self

    def __iter__(self) -> Iterator[dict]:
        self.load_cache()
        instance = QueryDict(self.response_data)

        if self.search_instance.path_to_items is None:
            raise ValueError('Should set path to items')

        queryset = instance.filter(self.search_instance.path_to_items)
        items = self.search_instance.result_generator(queryset)
        for item in items:
            yield item

    @cached_property
    def data(self) -> dict[str, str] | None:
        # async_to_sync(self.load_cache)()
        self.load_cache()
        return self.response_data

    def load_cache(self):
        if self.response_data:
            return

        if self.search_instance is not None:
            session, request = self.search_instance.create_request()

            try:
                response = session.send(request)
            except:
                raise Exception('Could not send request')
            else:
                self.response_data = response.json()

    async def next(self):
        pass


class BaseSearch(Generic[Q]):
    response_data = None
    results = []
    results_iterator = ResultsIterator()

    def __init__(self, query: str, limit: int = 10, language: str = 'en', region: str = 'US', search_preferences: Optional[str] = None, timeout: Optional[int] | None = None):
        self.query = query
        self.limit = limit
        self.language = language
        self.region = region
        self.search_preferences = search_preferences
        self.timeout = timeout
        self.continuation_key = None
        # The path to the list of items that
        # we are interested in a__b__c
        self.path_to_items = None

    @property
    def request_payload(self) -> D:
        return {
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

    @property
    def url(self):
        encoded_key = urlencode({'key': SEARCH_KEY})
        return f'https://www.youtube.com/youtubei/v1/search?{encoded_key}'

    def result_generator(self, queryset: Q) -> list:
        """Custom class used to generate the results
        for the given class"""
        return []

    def create_request(self):
        session = Session()

        payload = self.request_payload.copy()
        payload['query'] = self.query
        payload['client'] = {
            'hl': self.language,
            'gl': self.region
        }

        if self.search_preferences:
            payload['params'] = self.search_preferences

        if self.continuation_key is not None:
            payload['continuation'] = self.continuation_key

        data = json.dumps(payload).encode('utf-8')

        params = {
            'method': 'post',
            'url': self.url,
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

    # async def send(self):
    #     session, request = self.create_request()

    #     try:
    #         response = session.send(request)
    #     except:
    #         raise Exception('Could not send request')
    #     else:
    #         self.response_data = response.json()


class Search(BaseSearch):
    def __init__(self, query: str, *, limit: int = 20, **kwargs: str | int):
        self.search_mode = (True, True, True)
        super().__init__(query, limit, **kwargs)


class Videos(BaseSearch):
    def __init__(self, query: str, *, limit: int = 20, **kwargs: str):
        self.search_mode = (True, True, True)
        super().__init__(query, limit, search_preferences=SearchModes.videos, **kwargs)
        self.path_to_items = 'contents__twoColumnSearchResultsRenderer__primaryContents__sectionListRenderer__contents'

    def result_generator(self, queryset: Query) -> Iterator[dict]:
        for item in queryset:
            if 'itemSectionRenderer' in item:
                for content in item['itemSectionRenderer']['contents']:
                    value = content.get('videoRenderer', None)
                    if value is None:
                        continue

                    yield {
                        'video_id': value['videoId'],
                        'thumbnail': value['thumbnail'],
                        'title': value['title']['runs'][-1]['text'],
                        'publication_text': value['publishedTimeText']['simpleText'],
                        'duration': value['lengthText']['simpleText'],
                        'view_count_text': value['viewCountText']['simpleText'],
                        'search_key': value['searchVideoResultEntityKey']
                    }
            elif 'continuationItemRenderer' in item:
                continue


class Channels(BaseSearch):
    pass


class Playlists(BaseSearch):
    pass


class ChannelVideos(BaseSearch):
    pass


class Custom(BaseSearch):
    pass


# base_search = Videos('Watermelon Sugar', limit=1)
# # async_to_sync(base_search.send)()
# # base_search.results_iterator.load_cache()

# with open('./tests/data/video_search.json', mode='w', encoding='utf-8') as f:
#     json.dump(base_search.results_iterator.data, f)
