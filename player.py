from enum import Enum
from time import sleep
from urllib import parse
from kthread import KThread
from threading import Thread
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
import pickle

class PlayerTrack:
    def __init__(self, keyword: str, track: Track = None, audio_stream: FFmpegPCMAudio = None):
        self.keyword = keyword
        self.track = track
        self.audio_stream = audio_stream
        
    def playable(self) -> bool:
        return self.audio_stream is not None and self.track is not None

    def get_serialized_format(self):
        return pickle.loads(self)
        
class MusicPlayer:
    def __init__(self, bot: Bot):
        self.__queue = list()
        self.sleep_time = 3
        self._state = PlayerState.IDLE
        self.bot = bot
        self.ctx: Context = None
        self.voice_client: VoiceClient = None
        self.current_track: PlayerTrack = None
        self.dc_task_queued = False
        self.dc_timer_threshold = 60 * 5

        # Player Loop is multithreaded, each guild will have separate thread
        self.loop_thread = KThread(target=self.loop, name="Main Loop Thread")
        self.loop_thread.start()
        
        self.dc_timer = None

    @property
    def queue(self):
        return self.__queue
    
    def is_connected_and_idle(self) -> bool:
        return len(self.__queue) == 0 and self.voice_client is not None and self._state == PlayerState.IDLE and not self.dc_task_queued

    def has_song_in_queue(self):
        return len(self.queue) > 0
    
    def dequeue_track(self) -> PlayerTrack:
        print('Dequeing the first song')
        self.current_track = self.queue.pop(0)

        # Get the correct extractor from the factory
        extractor = get_extractor(self.current_track.keyword)

        # Extract the contents from appropriate API
        extracted_data = extractor.extract_track(self.current_track.keyword)

        # If the data returned is a playlist then iterate over all the data and add them into the queue
        if extractor.is_playlist(extracted_data):
            for artist, track in extracted_data.items():
                self.queue.append(PlayerTrack(f'{track} - {artist}'))
            
            # After adding all the data to queue take the first one and extract information about it
            self.current_track = self.queue.pop(0)
            self.current_track.track = get_extractor(self.current_track.keyword).extract_track(self.current_track.keyword)
        
        # Else if the data returned is a track simply assign the value back to self.current_track and return it
        else:
            self.current_track.track = extracted_data

        self.current_track.audio_stream = FFmpegPCMAudio(self.current_track.track.stream_url, **FFMPEG_OPTIONS)
        return self.current_track
    
    def add_track(self, ctx: Context, keyword: str) -> None:
        self.ctx, self.voice_client = ctx, ctx.voice_client
        self.__queue.append(PlayerTrack(keyword))

    def queue_repeat_request(self) -> None:
        if self.current_track is not None:
            self.__queue.append(self.current_track)
            return True
        return False
        
    # Reset any state variables here
    def reset_state(self) -> None:
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
        
    def start_dc_timer(self) -> None:
        print('Started DC Timer for guild: ', self.ctx.guild.name)  
        timer = 0
        
        try:
            while True:
                print(f'Counting {timer}')
                
                # If a song is added between the timer
                if len(self.__queue) > 0:
                    self.dc_task_queued = False
                    self.dc_timer.terminate()
                    return
                    
                # If the timer reaches it's dc threshold disconnect from the guild
                # TODO: Too many variables being assigned here, find a better approach
                if timer >= self.dc_timer_threshold:
                    print('Timer reached, disconnecting from guild {}'.format(self.ctx.guild.name))
                    self.leave()
                    del players[self.ctx.guild.id]
                    self.dc_task_queued = False
                    return
                timer += 1
                sleep(1)
        except:
            print('[DEBUG] Song was queued in between, breaking out of thread')

    def loop(self) -> None:
        while not self.bot.is_closed():
            if self.has_song_in_queue() and self._state == PlayerState.IDLE:
                try:
                    requested_track: PlayerTrack = self.dequeue_track()
                    self.voice_client.play(requested_track.audio_stream, after=lambda e: self.reset_state())
                    self.bot.loop.create_task(self.ctx.send(embed=get_music_embed(requested_track.track)))
                    self._state = PlayerState.PLAYING
                except Exception as e:
                    print(str(e))
                    continue
            else:
                '''
                # TODO: The auto disconnect timer has some bugs
                if self.is_connected_and_idle():
                    self.dc_task_queued = True
                    self.dc_timer = KThread(target=self.start_dc_timer)
                    self.dc_timer.start()
                '''
                sleep(self.sleep_time)

players: Dict[int, MusicPlayer] = dict()

# Manager class for all MusicPlayers. It acts as an proxy between client commands and MusicPlayer class.
# Do not create instances or modify music players by yourself, use this class to get your specific guild player. 
class MusicPlayerManager:
    def __init__(self) -> None: ...

    def get_current_song(self, id: int) -> PlayerTrack:
        return self.get_guild_player(id).current_track

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
        
    def reset_guild_player(self, id: int) -> None:
        guild_player = self.get_guild_player(id)
        if guild_player.voice_client: 
            guild_player.voice_client.stop()
        guild_player.clear_queue()
        guild_player.reset_state()
        
    def register_repeat_request(self, id: int) -> None:
        if self.get_guild_player(id).queue_repeat_request():
            return True
        return False

    def is_guild_player_registered(self, id: int) -> bool:
        return id in players

    def register_guild_player(self, id: int, player) -> bool:
        players[id] = player
