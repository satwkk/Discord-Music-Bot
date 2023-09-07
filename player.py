from enum import Enum
from time import sleep
from typing import Dict
from typing import List
from urllib import parse
from discord import Guild
from threading import Thread
from models.track import Track
from discord import VoiceClient
from discord.ext.commands import Bot
from discord import FFmpegPCMAudio

# Importing all the extractors
from extractors.base_player import Player
from extractors.default_player import DefaultPlayer
from extractors.youtube_player import YoutubeTrackPlayer
from extractors.spotify_player import SpotifyTrackPlayer, SpotifyPlaylistPlayer, SpotifyAlbumPlayer

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class PlayerState(Enum):
    IDLE=0
    PLAYING=1

# A factory to get the player based on player's request.
# If the request is keyword then it performs a youtube search
# Else it takes the url and uses the api based on the domain of the url
def get_extractor(keyword: str) -> Player:
    if keyword.startswith('http'):
        url_comp = parse.urlsplit(keyword)
        match (url_comp.netloc):
            case "open.spotify.com":
                if 'track' in url_comp.path:
                    return SpotifyTrackPlayer()
                elif 'album' in url_comp.path:
                    return SpotifyAlbumPlayer()
                elif 'playlist' in url_comp.path:
                    return SpotifyPlaylistPlayer()
            case "www.youtube.com":
                if 'watch' in url_comp.path:
                    return YoutubeTrackPlayer()
    return DefaultPlayer()

# Main player Loop class which handles all music related functionalities.
# NOTE: Do not create instance of this class separately, instead handle it through the PlayerManager class.
class MusicPlayer:
    def __init__(self, bot: Bot):
        self.__queue = list()
        self.bot = bot
        self.current_track: Track = None
        self.voice_client: VoiceClient = None
        self.state = PlayerState.IDLE
        
        # Player Loop is multithreaded, each guild will have separate thread
        l = Thread(target=self.loop)
        l.daemon = True
        l.start()
        
    @property
    def queue(self):
        return self.__queue
    
    def dequeue_track(self, out_audio_stream: bytes) -> None:
        print('Dequeing the first song')
        self.current_track = self.__queue.pop(0)
        track = get_extractor(self.current_track).extract_track(self.current_track)
        audio_stream = FFmpegPCMAudio(track.stream_url, **FFMPEG_OPTIONS)
        print(track, out_audio_stream)
        return audio_stream
    
    def add_track(self, ctx, keyword):
        self.voice_client = ctx.voice_client
        self.__queue.append(keyword)
        
    def reset_state(self):
        print('Resetting state')
        self.state = PlayerState.IDLE
        
    def clear_queue(self):
        self.__queue.clear()
        
    def skip_track(self):
        self.voice_client.stop()
        
    def loop(self):
        while not self.bot.is_closed():
            if len(self.__queue) > 0 and self.state == PlayerState.IDLE:
                print('true')
                audio_stream: bytes = self.dequeue_track(None)
                self.voice_client.play(audio_stream, after=lambda e: self.reset_state())
                self.state = PlayerState.PLAYING
            else:
                # Sleep for 1 second
                print('false')
                sleep(5)
            
players: Dict[int, MusicPlayer] = dict()

class MusicPlayerManager:
    def __init__(self) -> None:
        pass
            
    def set_guild_player(self, bot: Bot, guild: Guild) -> None:
        players[guild.id] = Player(bot)
        
    @staticmethod
    def set_guild_players(bot: Bot, guilds: List[Guild]) -> None:
        for guild in guilds: 
            print(guild.id)
            players[guild.id] = MusicPlayer(bot)
                
    def get_guild_player(self, id: int) -> MusicPlayer:
        return players[id]
    
    def print_players_DEBUG(self) -> None:
        print(players)
            
    def get_guild_queue_list(self, id: int) -> List[Track]:
        return players[id].queue
    
    def clear_guild_queue_list(self, id: int) -> None:
        players[id].clear_queue()
        
    def skip_guild_track(self, id: int) -> None:
        players[id].skip_track()
        