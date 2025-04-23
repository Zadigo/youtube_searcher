from typing import TYPE_CHECKING, Dict, TypeVar, Mapping, Union, Protocol, runtime_checkable

if TYPE_CHECKING:
    from youtube_searcher.query import Query, QueryList
    from youtube_searcher.search import BaseSearch
    from youtube_searcher.models.videos import VideoModel, ThumbnailModel

B = TypeVar('B', bound='BaseSearch')

Q = TypeVar('Q', bound='Query')

QL = TypeVar('QL', bound='QueryList')

NestedJson = Union[str, int, bool, Dict[str, 'D']]
D = Mapping[str, NestedJson]


@runtime_checkable
class BaseModelProtocol(Protocol):
    def __init__(self, **kwargs: object) -> None:
        ...


DC = TypeVar('DC', bound=BaseModelProtocol)
