from functools import cached_property
from typing import Generic, Iterator, Optional, Type

from youtube_searcher.typings import B, D, DC


class Query(Generic[B]):
    def __init__(self, data: D):
        self.initial_data: D = data
        self.queried_data: Optional[list[D]] = None

    def __repr__(self):
        return f'<QueryDict[{self.queried_data}]>'

    def __item__(self, key: str):
        return self.initial_data.get(key, None)


class QueryDict(Query):
    """A helper class used to query the complex
    dicts returned by the response"""

    def filter(self, query_path: str):
        """Function used to match certain values in
        the response data"""
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

    def __item__(self, index: int):
        return self.initial_data[index]


class ResultsIterator(Generic[B, DC]):
    def __init__(self):
        self.search_instance: Optional[B] = None
        self.response_data: Optional[D] = None

    def __get__(self, instance: B, cls: Optional[Type[B]] = None):
        self.search_instance = instance
        return self

    def __iter__(self) -> Iterator[DC]:
        self.load_cache()
        instance = QueryDict(self.response_data)

        if self.search_instance.path_to_items is None:
            raise ValueError('Should set path to items')

        queryset = instance.filter(self.search_instance.path_to_items)
        items = self.search_instance.result_generator(queryset)

        if self.search_instance.model is None:
            raise ValueError('model cannot be None')

        for item in items:
            yield self.search_instance.model(**item)

    @cached_property
    def data(self) -> dict[str, str] | None:
        self.load_cache()
        return self.response_data

    def load_cache(self):
        """Method that sends the request to YouTube
        in order to get the searched results"""
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

            if 'estimatedResults' in self.response_data:
                value = self.response_data['estimatedResults']
                self.search_instance.estimated_results = int(value)

    async def next(self):
        pass
