import json
from functools import cached_property, lru_cache
from typing import Dict, Generic, Mapping, Optional, Type, TypeVar, Union
from urllib.parse import urlencode

from asgiref.sync import async_to_sync
from requests import Request, Session

from youtubing.constants import SEARCH_KEY, USER_AGENT, SearchModes

B = TypeVar('B', bound='BaseSearch')

NestedJson = Union[str, int, bool, Dict[str, 'D']]
D = Mapping[str, NestedJson]


class QueryDict:
    """A helper class that can query a complex
    dictionnary up to a certain point"""

    def __init__(self, data: NestedJson, query_path: str):
        self.keys = query_path.split('__')

        result = None
        for key in self.keys:
            if result is None:
                is_valid = self.check(key, data)
                if is_valid:
                    result = data[key]
            else:
                is_valid = self.check(key, data)
                if is_valid:
                    result = result[key]

    @staticmethod
    def check(key: str, data: NestedJson):
        """A function that indicates wether the item is a
        dictionnary and therefore abled to be keyed"""
        value = data[key]
        if isinstance(value, str):
            return False
        elif isinstance(value, int):
            return False
        else:
            return True


class ResultsIterator(Generic[B]):
    def __init__(self):
        self.instance: B | None = None
        self.response_data: dict[str, str] | None = None

    @cached_property
    def data(self) -> dict[str, str] | None:
        async_to_sync(self.load_cache)()
        return self.response_data

    def __get__(self, instance: B, cls: Optional[Type[B]] = None):
        self.instance = instance
        return self

    def __iter__(self):
        async_to_sync(self.load_cache)()
        return iter([])

    async def load_cache(self):
        if self.instance is not None:
            session, request = self.instance.create_request()

            try:
                response = session.send(request)
            except:
                raise Exception('Could not send request')
            else:
                self.response_data = response.json()

            # instance = QueryDict(self.response_data, self.instance.query_path)

    async def next(self):
        pass


class BaseSearch:
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
        self.query_path = None

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
        self.query_path = 'contents__twoColumnSearchResultsRenderer__primaryContents___richGridRenderer__contents'


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
