import inspect
from functools import cached_property
from typing import Generic, Iterator, Optional, Type
import dataclasses
from youtube_searcher.typings import DC, B, D


class Query(Generic[B]):
    def __init__(self, data: D):
        self.initial_data: D = data
        self.queried_data: Optional[D | list[D]] = None

    def __repr__(self):
        data = self.queried_data or self.initial_data
        return f'<QueryDict[{data}]>'

    def __getitem__(self, key: str):
        return self.initial_data.get(key, None)


class QueryDict(Query):
    """`QueryDict` traverses a complex dictionnary in
    order to return the subsection that we are
    interested in. For instance:

    >>> value = {'name': {'firstname': {'eu': 'Paul'}}}
    ... instance = QueryDict(value)
    ... instance.filter('name__firstname__eu')
    ... {'eu': 'Paul'}

    If the resulting element is a list, `QueryList` is returned
    which is essentially a list returning `QueryDict` instances
    """

    def __dict__(self):
        if self.queried_data and isinstance(self.queried_data, (dict, list)):
            return dict(self.queried_data)
        elif self.initial_data:
            return dict(self.initial_data)
        else:
            pass

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
        """A function that indicates wether the item that
        we are trying to query is a dictionnary and therefore
        has the ability to be traversed

        >>> value = {'name': 'Kendall'}
        ... instance = QueryDict(value)
        ... instance.check('name', value)
        ... False
        """
        # In the value is just a plain item,
        # don't bother raising an error just
        # return False
        if isinstance(data, (int, str, bool)):
            return False

        if inspect.isclass(data):
            data = data.__dict__

        if dataclasses.is_dataclass(data):
            data = dataclasses.asdict(data)

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
            # on the queried_data property
            self.queried_data = value
        else:
            return False


class QueryList(Query):
    """`QueryList` returns a list of `QueryDict`
    instances in order to traverse dictionnaries
    nested within a list

    >>> value = [{'name': 'Kendall'}]
    ... instance = QueryList(value)
    """

    def __init__(self, initial_data: list):
        super().__init__(initial_data)

    def __repr__(self):
        return f'<QueryList[{self.data}]>'

    def __iter__(self):
        for item in self.data:
            yield item

    def __getitem__(self, index: int):
        return self.data[index]

    def __len__(self):
        return len(self.data)

    @cached_property
    def data(self):
        items = []

        data_to_iterate = self.queried_data or self.initial_data

        for item in data_to_iterate:
            items.append(QueryDict(item))
        return items


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
            if isinstance(item, QueryDict):
                # If no query was performed on the initial data
                # return it even though it could raise an error
                # on the model that we are using
                item = item.queried_data or item.initial_data
            yield self.search_instance.model(**item)

    @cached_property
    def data(self) -> dict[str, str] | None:
        self.load_cache()
        return self.response_data

    def load_cache(self, refresh: bool = False):
        """Method that used to create and send the request 
        to YouTube search url. The results are stored in
        the cache of the class"""
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
