# Module imports
import discord
from urllib import parse
from discord.ext import commands

# Queue imports
from song_queue import init_queue, add_to_queue, get_guild_queue, enqueue_song, clear_queue

# Importing all the extractors
from extractors.base_player import Player
from extractors.default_player import DefaultPlayer
from extractors.youtube_player import YoutubeTrackPlayer, YoutubePlaylistPlayer
from extractors.spotify_player import SpotifyTrackPlayer, SpotifyPlaylistPlayer, SpotifyAlbumPlayer

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        
# A factory to get the player based on player's request.
# If the request is keyword then it performs a youtube search
# Else it takes the url and uses the api based on the domain of the url
def _get_player(keyword):
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

# Main music COG that manages all audio related commands
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # TODO: init_queue(ids) 
    
    async def _play(self, ctx, keyword):
        player = _get_player(keyword)
        track = await player.extract_track(keyword)
        audio_stream = await _convert_track_to_audio_stream(track)
        await ctx.send(f'Playing ▶️ **{track.title}**')
        ctx.voice_client.play(audio_stream, after=lambda e=None: self._play_next_song(ctx))
        
    def _play_next_song(self, ctx):
        track = enqueue_song(ctx.guild.id)
        self.bot.loop.create_task(self._play(ctx, track))
        
    @commands.command()
    async def play(self, ctx, *, keyword):
        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
            
        if ctx.voice_client.is_playing():
            add_to_queue(ctx.guild.id, keyword)
            return await ctx.send(f'Added **{keyword}** to queue.')
        
        self.bot.loop.create_task(self._play(ctx, keyword))
    
    @commands.command()
    async def skip(self, ctx):
        ctx.voice_client.stop()
    
    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client.is_playing(): ctx.voice_client.pause()
    
    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client.is_paused(): ctx.voice_client.resume()
    
    @commands.command()
    async def list_queue(self, ctx):
        temp_str = str()
        for idx, song in enumerate(get_guild_queue(ctx.guild.id)):
            temp_str += f'**{idx}. {song}**'
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
    
async def setup(bot):
    await bot.add_cog(Music(bot))
    
