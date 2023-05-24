import youtube_dl

from abc import ABC, abstractmethod

YOUTUBEDL_PARAMS = {'format': 'bestaudio/best', 'noplaylist':'True', 'quiet': 'True', 'ignoreerrors': 'True'}
YTDL_SEARCH_QUERY = "https://www.youtube.com/watch?v={}"

# Initializing youtube_dl client
ytdl = youtube_dl.YoutubeDL(params=YOUTUBEDL_PARAMS, auto_init=True)

# Base class
# NOTE: Should not be instantiated
class Player(ABC):
    def __init__(self): ...
    
    # This function takes the video id and extracts meta data about that video   
    def ytdl_search(self, input):
        info = ytdl.extract_info(
            YTDL_SEARCH_QUERY.format(input),
            download=False
        )
        return info
    
    @abstractmethod
    async def extract_track(self, keyword):
        print ('Base class extract_track called !!!')