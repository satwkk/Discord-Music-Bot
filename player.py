import time

from discord import Guild
from typing import List
from discord import VoiceClient, FFmpegOpusAudio
from models.track import Track
from threading import Thread
from discord.ext.commands import Bot
from time import sleep
from enum import Enum

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

class PlayerState(Enum):
    IDLE=0
    PLAYING=1

class Player:
    def __init__(self, bot: Bot):
        self.queue = list()
        self.bot = bot
        self.current_track = None
        self.voice_client = None
        self.state = PlayerState.IDLE
        l = Thread(target=self.loop)
        l.daemon = True
        l.start()
    
    def add_track(self, ctx, track):
        self.voice_client = ctx.voice_client
        self.queue.append(track)
        
    def reset_state(self):
        print('Resetting state')
        self.state = PlayerState.IDLE
        
    def loop(self):
        while not self.bot.is_closed():
            
            if len(self.queue) > 0 and self.state == PlayerState.IDLE:
                print('true')
                self.current_track = self.queue.pop(0)
                self.voice_client.play(self.current_track[1], after=lambda e: self.reset_state())
                self.state = PlayerState.PLAYING
                
            else:
                # Sleep for 1 second
                print('false')
                sleep(2)
            

from typing import Dict
players: Dict[int, Player] = dict()

class PlayerManager:
    def __init__(self) -> None:
        pass
            
    def set_guild_player(self, bot: Bot, guild: Guild) -> None:
        players[guild.id] = Player(bot)
        
    @staticmethod
    def set_guild_players(bot: Bot, guilds: List[Guild]) -> None:
        for guild in guilds: 
            print(guild.id)
            players[guild.id] = Player(bot)
                
    def get_guild_player(self, id: int) -> Player:
        return players[id]
    
    def print_players_DEBUG(self) -> None:
        print(players)
            
    def get_player_queue_list(self, id: int) -> List[Track]:
        return players[id].queue