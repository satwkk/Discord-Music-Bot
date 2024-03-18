from collections.abc import Callable, Iterable, Mapping
from typing import Any
import pytube
from kthread import KThread
from typing import Union, Dict, List

from models.track import Track
from extractors.base_player import Player

# Takes a youtube video url and extracts the audio from it to be streamed on discord.
class YoutubeTrackPlayer(Player):
    def __init__(self):
        super().__init__()
        
    def extract_track(self, url):
        result = pytube.YouTube(url)
        search_info = self.ytdl_search(result.video_id)
        return Track(
            search_info.get('uploader'),
            search_info.get('title'),
            search_info.get('url'),
            search_info.get('thumbnail')
        )
        
# TODO 
class YoutubePlaylistPlayer(Player):
    def __init__(self):
        super().__init__()