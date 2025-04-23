import datetime
from dataclasses import dataclass, field


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
    search_key: str
    thumbnails: list = field(default_factory=list)

    def __repr__(self):
        return f'<VideoModel [{self.video_id}]>'

    def __hash__(self):
        return hash((self.video_id,))
