import datetime
from dataclasses import dataclass, field

from youtube_searcher.utils import create_channel_link, create_youtube_link


@dataclass
class SimpleChannelModel:
    channel_id: str
    title: str
    youtube_link: str = None

    def __post_init__(self):
        if self.channel_id:
            self.youtube_link = create_channel_link(self.channel_id)

    def __repr__(self):
        return f'<VideoModel [{self.title}]>'

    def __hash__(self):
        return hash((self.channel_id,))


@dataclass
class ThumbnailModel:
    url: str = None
    width: int = None
    height: int = None


@dataclass
class VideoModel:
    title: str
    video_id: str
    publication_text: str
    duration: str
    view_count_text: str
    thumbnails: list[ThumbnailModel] = field(default_factory=list)
    search_key: str = None
    youtube_link: str = None
    youtube_channel: str = None
    channel: SimpleChannelModel = field(
        default_factory=lambda: SimpleChannelModel)
    description: str = None

    def __post_init__(self):
        if self.video_id:
            self.youtube_link = create_youtube_link(self.video_id)

    def __repr__(self):
        return f'<VideoModel [{self.title}]>'

    def __hash__(self):
        return hash((self.video_id,))
