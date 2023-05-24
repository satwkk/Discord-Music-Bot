import pytube

from models.track import Track
from extractors.base_player import Player

# Takes a youtube video url and extracts the audio from it to be streamed on discord.
class YoutubeTrackPlayer(Player):
    def __init__(self):
        super().__init__()
        
    async def extract_track(self, url):
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
        
    async def extract_track(self, keyword):
        ...