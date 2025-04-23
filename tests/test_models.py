from unittest import TestCase
import pathlib
from dataclasses import is_dataclass
from youtube_searcher.models.videos import VideoModel

TEST_DIR = pathlib.Path('.').joinpath('tests').absolute()


class TestVideoModel(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = [
            {
                "video_id": "J-G3DPx0pzE",
                "thumbnails": [
                    {
                        "url": "https: //i.ytimg.com/vi/J-G3DPx0pzE/hq720.jpg?sqp=-oaymwEcCOgCEMoBSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLAr2lW_WpxfLng0y579CJwNKaxA6A",
                        "width": 360,
                        "height": 202
                    },
                    {
                        "url": "https://i.ytimg.com/vi/J-G3DPx0pzE/hq720.jpg?sqp=-oaymwEcCNAFEJQDSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLA4zF-w9bnHhWYmXfZx8IPBu4mYKg",
                        "width": 720,
                        "height": 404
                    }
                ],
                "title": "Harry Styles - Watermelon Sugar (GRAMMYs Full Live Performance) 2021 HD",
                "publication_text": "4 years ago",
                "duration": "3:45",
                "view_count_text": "7,268,719 views",
                "search_key": "EgtKLUczRFB4MHB6RSDnAigB"
            }
        ]

    def test_structure(self):
        for item in self.data:
            result = VideoModel(**item)
            print(result)
