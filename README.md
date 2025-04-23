# YouTube Searcher

YouTube search is Python module that allows users to search YouTube on different levels. This project is a fork and adaptation from [Youtube Search](https://pypi.org/project/youtube-search/)
with advanced features for filtering and data manipulation.

## Searching Videos

### All

```python
from youtube_searcher.search import Videos

instance = Videos('Arlette pop the baloon', limit=2)
instance.objects.all()
```

The value returned by `all` is a list of dataclass models on which additional actions can be run upon.

## Values List

```python
from youtube_searcher.search import Videos

instance = Videos('Arlette pop the baloon', limit=2)
instance.objects.values_list('video_id', 'title')
```
