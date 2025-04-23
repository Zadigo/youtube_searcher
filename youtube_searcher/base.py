# from youtubesearchpython import VideosSearch

# videosSearch = VideosSearch('Jalousie Princess', limit=2)

# print(videosSearch.result())


from youtube_searcher.search import Videos


v = Videos('Arlette pop the baloon', limit=2)
print(v.objects.values_list('video_id', 'title'))
