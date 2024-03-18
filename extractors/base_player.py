from youtube_dl import YoutubeDL

from models.track import Track
from typing import Union, Dict, List
from abc import ABC, abstractmethod

YOUTUBEDL_PARAMS = {'format': 'bestaudio/best', 'noplaylist':'True', 'quiet': 'True', 'ignoreerrors': 'True', 'audio-quality': '0'}
YTDL_SEARCH_QUERY = "https://www.youtube.com/watch?v={}"

# Initializing youtube_dl client
ytdl = YoutubeDL(params=YOUTUBEDL_PARAMS, auto_init=True)

# Base class
# NOTE: Should not be instantiated
class Player(ABC):
    def __init__(self): ...
    
    # This function takes the video id and extracts meta data about that video   
    def ytdl_search(self, input, out_response: Union[Dict[str, str], List[str]] = None):
        info = ytdl.extract_info(
            YTDL_SEARCH_QUERY.format(input),
            download=False
        )
        return info
    
    @abstractmethod
    def extract_track(self, keyword) -> Union[Track, Dict[str, str]]:
        print ('Base class extract_track called !!!')
    
    def is_playlist(self, response_data) -> bool:
        return isinstance(response_data, dict)
    