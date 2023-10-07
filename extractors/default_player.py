import pytube

from models.track import Track
from extractors.base_player import Player

# Default player class that is used if the user performs a keyword based search
class DefaultPlayer(Player):
    def __init__(self):
        super().__init__()
        
    def extract_track(self, keyword):
        search_res = pytube.Search(keyword)
        search_info = self.ytdl_search(search_res.results[0].video_id)
        return Track(
            search_info.get('url'),
            search_info.get('uploader'),
            search_info.get('thumbnail'),
            search_info.get('title')
        )