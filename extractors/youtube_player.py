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
            search_info.get('url'),
            search_info.get('uploader'),
            search_info.get('thumbnail'),
            search_info.get('title')
        )
        
# TODO 
class YoutubePlaylistPlayer(Player):
    def __init__(self):
        super().__init__()

    def ytdl_search(self, video_id, out_response: Union[Dict[str, str], List[str]] =None):
        response = super().ytdl_search(video_id, out_response)
        out_response = response if isinstance(out_response, dict) else out_response.append(response)
    
    def extract_track(self, keyword: str):
        playlist = pytube.Playlist(keyword)
        videos = playlist.videos

        responses: List[str] = list()
        thread_pool: List[KThread] = []

        for video in videos:
            thread = KThread(self.ytdl_search, args=(video.video_id, responses))
            thread_pool.append(thread)
            thread.start()

        finished = False
        for t in thread_pool:
            if not t.is_alive(): finished = True
            else: finished = False
        
        if finished: return responses