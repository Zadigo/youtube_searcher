USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'

VIDEO_ELEMENT_KEY = 'videoRenderer'

CHANNEL_ELEMENT_KEY = 'channelRenderer'

PLAYLIST_ELEMENT_KEY = 'playlistRenderer'

SHELF_ELEMENT_KEY = 'shelfRenderer'

ITEM_SECTION_KEY = 'itemSectionRenderer'

CONTINUATION_ITEM_KEY = 'continuationItemRenderer'

PLAYER_RESPONSE_KEY = 'playerResponse'

RICH_ITEM_KEY = 'richItemRenderer'

HASHTAG_ELEMENT_KEY = 'hashtagTileRenderer'

HASHTAG_BROWSE_KEY = 'FEhashtag'

HASHTAG_VIDEOS_PATH = [
    'contents', 'twoColumnBrowseResultsRenderer',
    'tabs', 0, 'tabRenderer', 'content', 'richGridRenderer', 'contents']

HASHTAG_CONTINUATION_VIDEOS_PATH = [
    'onResponseReceivedActions', 0,
    'appendContinuationItemsAction', 'continuationItems'
]

SEARCH_KEY = 'AIzaSyAO_FJ2SlqU8Q4STEHLGCilw_Y9_11qcW8'

CONTENT_PATH = [
    'contents', 'twoColumnSearchResultsRenderer',
                'primaryContents', 'sectionListRenderer', 'contents'
]

FALLBACK_CONTENT_PATH = [
    'contents', 'twoColumnSearchResultsRenderer',
    'primaryContents', 'richGridRenderer', 'contents'
]

CONTINUATION_CONTENT_PATH = [
    'onResponseReceivedCommands',
    0, 'appendContinuationItemsAction', 'continuationItems'
]

CONTINUATION_KEY_PATH = [
    'continuationItemRenderer',
    'continuationEndpoint', 'continuationCommand', 'token'
]

PLAYLIST_INFO_PATH = [
    'response', 'sidebar',
    'playlistSidebarRenderer', 'items'
]

PLAYLIST_VIDEOS_PATH = [
    'response', 'contents', 'twoColumnBrowseResultsRenderer',
    'tabs', 0, 'tabRenderer', 'content', 'sectionListRenderer',
    'contents', 0, 'itemSectionRenderer', 'contents', 0,
    'playlistVideoListRenderer', 'contents'
]

PLAYLIST_PRIMARY_INFO_KEY = 'playlistSidebarPrimaryInfoRenderer'

PLAYLIST_SECONDARY_INFO_KEY = 'playlistSidebarSecondaryInfoRenderer'

PLAYLIST_VIDEO_KEY = 'playlistVideoRenderer'


class SearchModes:
    videos = 'EgIQAQ%3D%3D'
    channels = 'EgIQAg%3D%3D'
    playlists = 'EgIQAw%3D%3D'
    livestreams = 'EgJAAQ%3D%3D'
