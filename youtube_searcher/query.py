import dataclasses
import inspect
from collections import OrderedDict, defaultdict
from functools import cached_property
from typing import Generic, Iterator, Optional, Type, Union

from youtube_searcher.typings import DC, QL, B, D


class Query(Generic[B]):
    def __init__(self, data: Union[D, list[D]]):
        self.cache: Union[D, list[D]] = data

    def __repr__(self):
        return f'<QueryDict[{self.cache}]>'

    def filter(self, query_path: str):
        """Function used to traverse the keys within
        a dictionnary returning the specific value stored
        under the last key of the path"""
        return NotImplemented

    def get(self, key_or_path: str):
        """Function used to get the value stored under
        a specific key in the dictionnary"""
        return NotImplemented


class QueryDict(Query):
    """`QueryDict` traverses a complex dictionnary in
    order to return the subsection that we are
    interested in. For instance:

    >>> value = {'name': {'firstname': {'eu': 'Paul'}}}
    ... instance = QueryDict(value)
    ... instance.filter('name__firstname__eu')
    ... {'eu': 'Paul'}

    If the resulting element is a list, `QueryList` is returned
    which is essentially a list returning `QueryDict` instances.

    Important note, the role of the path is not to return the value
    of the last key but the object of the target element. For example
    a `location__country` path in `{'location': {'country': 'USA'}}` will 
    not return "USA" but the block that contains the key "country" therefore
    `{'country': 'USA'}` is the expected result
    """

    def __contains__(self, value: str | int):
        return value in self.cache

    def __getitem__(self, key: str):
        return self.cache[key]

    @classmethod
    def new(cls, data):
        return cls(data)

    def get(self, key_or_path):
        if '__' in key_or_path:
            key = key_or_path.split('__')[-1]
            query_dict = self.filter(key_or_path)
            return query_dict[key]
        return self.cache[key_or_path]

    def filter(self, query_path: str):
        """Function used to match certain values in
        the response data"""
        self.keys = query_path.split('__')

        queried_data: D | None = None

        for key in self.keys:
            if queried_data is None:
                is_valid, value = self.check(key, self.cache)
                if is_valid:
                    queried_data = value
            else:
                is_valid, value = self.check(key, queried_data)
                if is_valid:
                    queried_data = queried_data[key]
                elif isinstance(value, list):
                    # if the return value is a list
                    # we do not iterate the list but
                    # prefer a list iteraotr: QueryList
                    queried_data = value
                    break

        if isinstance(queried_data, list):
            return QueryList(queried_data)
        return QueryDict.new(queried_data)

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
            return False, data

        if inspect.isclass(data):
            data = data.__dict__

        if dataclasses.is_dataclass(data):
            data = dataclasses.asdict(data)

        try:
            value = data[key]
        except KeyError:
            print(f'Warning: Could not get {key} from: {data}')
            return False, []
        else:
            if isinstance(value, str):
                return False, value
            elif isinstance(value, int):
                return False, value
            elif isinstance(value, dict):
                return True, value
            elif isinstance(value, list):
                return False, value
            return False, value


class QueryList(Query):
    """`QueryList` returns a list of `QueryDict`
    instances in order to traverse dictionnaries
    nested within a list

    >>> value = [{'name': 'Kendall'}]
    ... instance = QueryList(value)
    """

    def __init__(self, initial_data: list[D]):
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
    def data(self) -> list[QueryDict]:
        """Returns the elements of the
        cache as list of `QueryDict` instances"""
        items = []
        for item in self.cache:
            items.append(QueryDict(item))
        return items

    def filter(self, query_path: str) -> list[QueryDict]:
        items = []
        for item in self.data:
            items.append(item.filter(query_path))
        return items

    def last(self):
        return self.data[-1]

    def first(self):
        return self.data[-0]


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

        # Full clean can modify the initial query dict
        # instance by returning a different one
        instance = self.search_instance.full_clean(instance)
        if instance is None:
            raise ValueError('Full clean should return a value')

        if not isinstance(instance, QueryDict):
            raise ValueError('Full clean return value should be a QueryDict')

        if self.search_instance.path_to_items is None:
            raise ValueError('Should set path to items')

        queryset = instance.filter(self.search_instance.path_to_items)
        items = self.search_instance.result_generator(queryset)

        if self.search_instance.model is None:
            raise ValueError('model cannot be None')

        for item in items:
            if isinstance(item, QueryDict):
                item = item.cache
            yield self.search_instance.model(**item)

    @cached_property
    def data(self) -> dict[str, str] | None:
        self.load_cache()
        return self.response_data

    def all(self) -> list[DC]:
        return list(self)

    def values_list(self, *fields):
        """Returns a subset of values matching the given
        fields from the dataset

        >>> instance = Videos('Arlette pop the baloon', limit=2)
        ... instance.objects.values_list('video_id', 'title')
        ... [OrderedDict({'video_id': 'MVkuHKIPWgs', 'title': 'Ep 51'})]
        """
        fields = list(fields)

        def dict_generator(fields_to_use: list[str]):
            for item in self.all():
                data = OrderedDict()

                if not fields_to_use:
                    fields_to_use = map(
                        lambda x: x.name,
                        dataclasses.fields(item)
                    )

                for field in fields_to_use:
                    if '__' in field:
                        lhv, rhv = field.split('__')
                        relationship = getattr(item, lhv)
                        data[field] = getattr(relationship, rhv)
                        continue

                    data[field] = getattr(item, field)
                yield data
        return list(dict_generator(fields))

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
