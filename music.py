# Module imports
import discord
from cache import cache
from urllib import parse
from discord import Embed
from discord import Colour
from discord.ext import commands

# Queue imports
from song_queue import enqueue_song, get_guild_queue, dequeue_song, clear_queue

# TODO: Only debug remove later
from song_queue import global_queue
from cache import cache_track

# Importing all the extractors
from extractors.base_player import Player
from extractors.default_player import DefaultPlayer
from extractors.youtube_player import YoutubeTrackPlayer, YoutubePlaylistPlayer
from extractors.spotify_player import SpotifyTrackPlayer, SpotifyPlaylistPlayer, SpotifyAlbumPlayer

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        
# A factory to get the player based on player's request.
# If the request is keyword then it performs a youtube search
# Else it takes the url and uses the api based on the domain of the url
def get_extractor(keyword):
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

# Converts an opus audio to audio stream that can be streamed on discord
async def _convert_track_to_audio_stream(track):
    audio_stream = await discord.FFmpegOpusAudio.from_probe(track.stream, **FFMPEG_OPTIONS)
    return audio_stream

def validate_command_invoker(ctx):
    return ctx.author.voice.channel is not None

def author_callable(func):
    def wrapper(*args, **kwargs):
        ctx = args[1]
        if ctx.message.author.id != '':
            return ctx.send('You cannot invoke this command')
        func(*args, **kwargs)
    return wrapper

# Main music COG that manages all audio related commands
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _is_playing(self, vc): return vc.is_playing()
    def _is_paused(self, vc): return vc.is_paused()
    def _is_vc_active(self, vc): return self._is_playing(vc) or self._is_paused(vc)
    def _is_playlist(self, track): return isinstance(track, dict)
    def _is_joined_to_vc(self, vc): return vc is not None
    def _is_in_same_voice_channel_as_invoker(self, vclient, invoker): return invoker.voice.channel == vclient.channel

    @cache_track
    async def get_track_from_extractor(self, ctx, keyword):
        track = await get_extractor(keyword).extract_track(keyword)
        # If the data extactor is a dict, or a list of songs
        # then it is a playlist, hence add all the songs to the queue
        if self._is_playlist(track):
            enqueue_song(ctx.guild.id, track)
            # The data enqueued is still just a formated string, extracting meta data from the default player API.
            track = await DefaultPlayer().extract_track(dequeue_song(ctx.guild.id))
        return track

    async def play_song(self, ctx, keyword):
        track = await self.get_track_from_extractor(ctx, keyword)
        audio_stream = await _convert_track_to_audio_stream(track)
        
        track_embed = Embed(title='Playing ▶️', colour=discord.Colour.random())
        track_embed.add_field(name=f'{track.title}', value='\u200b')
        track_embed.set_thumbnail(url=track.thumbnail)
        await ctx.send(embed=track_embed)
        
        # await ctx.send(f'Playing ▶️ **{track.title}**')
        ctx.voice_client.play(audio_stream, after=lambda e=None: self.play_next_song(ctx))
        
    def play_next_song(self, ctx):
        track = dequeue_song(ctx.guild.id)
        self.bot.loop.create_task(self.play_song(ctx, track))
        
    @commands.command()
    @commands.check(validate_command_invoker)
    async def play(self, ctx, *, keyword):
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
            
        # Temporary check for url, will update it later
        if (ctx.voice_client.is_playing() or len(get_guild_queue(ctx.guild.id)) > 0) and not keyword.startswith('http'):
            enqueue_song(ctx.guild.id, keyword)
            return await ctx.send(f'Added **{keyword}** to queue.')
        
        self.bot.loop.create_task(self.play_song(ctx, keyword))
    
    @commands.command()
    async def skip(self, ctx):
        ctx.voice_client.stop()
    
    @commands.command()
    async def pause(self, ctx):
        if self._is_playing(ctx.voice_client): ctx.voice_client.pause()
    
    @commands.command()
    async def resume(self, ctx):
        if self._is_paused(ctx.voice_client): ctx.voice_client.resume()
    
    @commands.command()
    async def flush(self, ctx):
        clear_queue(ctx.guild.id)

    @commands.command()
    async def list_queue(self, ctx):
        temp_str = str()
        for idx, song in enumerate(get_guild_queue(ctx.guild.id)):
            temp_str += f'**{idx+1}. {song}**\n'
        await ctx.send(temp_str)
        
    @commands.command()
    async def leave(self, ctx):
        clear_queue(ctx.guild.id)
        await ctx.voice_client.disconnect()
        
    @commands.command()
    async def stop(self, ctx):
        clear_queue(ctx.guild.id)
        ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
    
    @commands.command()
    async def debug(self, ctx):
        print(global_queue)
        print(cache)

    @commands.command()
    async def chat(self, ctx, *, message):
        pass

    @commands.command()
    async def recommend_movie(self, ctx, *, keywords): 
        pass

async def setup(bot):
    await bot.add_cog(Music(bot))
    
