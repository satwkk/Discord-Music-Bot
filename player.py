from enum import Enum
from time import sleep
from urllib import parse
from kthread import KThread
from typing import List, Dict
from models.track import Track
from embeds import get_music_embed
from discord.ext.commands import Bot
from discord import Guild, VoiceClient, FFmpegPCMAudio

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
from discord.ext.commands import Context

class PlayerTrack:
    def __init__(self, keyword: str, track: Track = None, audio_stream: FFmpegPCMAudio = None):
        self.keyword = keyword
        self.track = track
        self.audio_stream = audio_stream
        
    def playable(self) -> bool:
        return self.audio_stream is not None and self.track is not None
        
class MusicPlayer:
    def __init__(self, bot: Bot):
        self.__queue = list()
        self.sleep_time = 5
        self._state = PlayerState.IDLE
        self.bot = bot
        self.repeat_current_track = False
        self.ctx: Context = None
        self.voice_client: VoiceClient = None
        self.current_track_2: PlayerTrack = None

        # Player Loop is multithreaded, each guild will have separate thread
        self.loop_thread = KThread(target=self.loop, name="Main Loop Thread")
        self.loop_thread.start()

    @property
    def queue(self):
        return self.__queue
    
    def dequeue_track(self) -> PlayerTrack:
        print('Dequeing the first song')
        self.current_track_2 = self.__queue.pop(0)
        self.current_track_2.track = get_extractor(self.current_track_2.keyword).extract_track(self.current_track_2.keyword)
        self.current_track_2.audio_stream = FFmpegPCMAudio(self.current_track_2.track.stream_url, **FFMPEG_OPTIONS)
        return self.current_track_2
    
    def add_track(self, ctx: Context, keyword: str) -> None:
        self.ctx, self.voice_client = ctx, ctx.voice_client
        self.__queue.append(PlayerTrack(keyword))

    def queue_repeat_request(self) -> None:
        if self.current_track_2 is not None:
            self.__queue.append(self.current_track_2)
            return True
        return False
        
    # Reset any state variables here
    def reset_state(self) -> None:
        self.repeat_current_track = False
        self._state = PlayerState.IDLE
        
    def clear_queue(self) -> None:
        self.__queue.clear()
        
    def skip_track(self) -> None:
        if self.voice_client is not None: self.voice_client.stop()
        
    def pause_track(self) -> None:
        if self.voice_client is not None: self.voice_client.pause()
        
    def resume_track(self) -> None:
        if self.voice_client is not None: self.voice_client.resume()
    
    def cleanup(self) -> None:
        self.voice_client = None
        self.loop_thread.terminate()

    def leave(self) -> None:
        self.queue.clear()
        self.bot.loop.create_task(self.voice_client.disconnect())
        self.loop_thread.terminate()

    def loop(self) -> None:
        while not self.bot.is_closed():
            if len(self.__queue) > 0 and self._state == PlayerState.IDLE:# or self.repeat
                try:
                    requested_track: PlayerTrack = self.dequeue_track()
                    self.voice_client.play(requested_track.audio_stream, after=lambda e: self.reset_state())
                    self.bot.loop.create_task(self.ctx.send(embed=get_music_embed(requested_track.track)))
                    self._state = PlayerState.PLAYING
                except Exception as e:
                    print(str(e))
                    continue
            else:
                sleep(self.sleep_time)

players: Dict[int, MusicPlayer] = dict()

# Manager class for all MusicPlayers. It acts as an proxy between client commands and MusicPlayer class.
# Do not create instances or modify music players by yourself, use this class to get your specific guild player. 
class MusicPlayerManager:
    def __init__(self) -> None: ...

    def contains_guild_player(self, id: int) -> bool:
        return True if id in players else False

    def remove_guild_player(self, id: int) -> None:
        if id not in players: return
        del players[id]
                
    def get_guild_player(self, id: int) -> MusicPlayer:
        return players[id]
    
    def print_players_DEBUG(self) -> None:
        print(players)
            
    def get_guild_queue(self, id: int) -> List[PlayerTrack]:
        return players[id].queue
    
    def clear_guild_queue(self, id: int) -> None:
        players[id].clear_queue()
        
    def skip_guild_track(self, id: int) -> None:
        players[id].skip_track()
        
    def leave_guild(self, id: int) -> None:
        self.get_guild_player(id).leave()
        self.remove_guild_player(id)
        
    def pause_guild_track(self, id: int) -> None:
        self.get_guild_player(id).pause_track()
        
    def resume_guild_track(self, id: int) -> None:
        self.get_guild_player(id).resume_track()
        
    def register_repeat_request(self, id: int) -> None:
        if self.get_guild_player(id).queue_repeat_request():
            return True
        return False
        
