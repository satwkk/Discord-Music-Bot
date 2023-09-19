from discord.ext import commands
from discord.ext.commands import Bot, Context
from player import MusicPlayerManager
from embeds import get_queue_embed
from player import players, MusicPlayer
from discord import Member

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
    def __init__(self, bot: Bot):
        self.bot = bot
        self.player_manager = MusicPlayerManager()

    @commands.command()
    @commands.check(validate_command_invoker)
    async def play(self, ctx: Context, *, keyword):
        if not ctx.voice_client: 
            await ctx.author.voice.channel.connect()

        await ctx.send(embed=get_queue_embed(keyword))
            
        if ctx.guild.id not in players:
            print('No guild player, creating one..')
            players[ctx.guild.id] = MusicPlayer(self.bot)

        print('Guild player found, getting the player...')
        guild_player = players[ctx.guild.id]
        guild_player.add_track(ctx, keyword)

    @commands.command()
    async def skip(self, ctx: Context):
        self.player_manager.skip_guild_track(ctx.guild.id)
    
    @commands.command()
    async def pause(self, ctx: Context):
        self.player_manager.pause_guild_track(ctx.guild.id)
    
    @commands.command()
    async def resume(self, ctx: Context):
        self.player_manager.resume_guild_track(ctx.guild.id)
        
    @commands.command()
    async def repeat(self, ctx: Context) -> None:
        if self.player_manager.register_repeat_request(ctx.guild.id): await ctx.send('Repeat request has been queued.')
        else: await ctx.send('Play a song to send repeat request.')
            
    @commands.command()
    async def flush(self, ctx: Context):
        self.player_manager.clear_guild_queue(ctx.guild.id)

    @commands.command()
    async def list_queue(self, ctx: Context):
        queue = self.player_manager.get_guild_queue(ctx.guild.id)
        temp_str = str()
        for idx, song in enumerate(queue):
            temp_str += f'**{idx+1}. {song.keyword}**\n'
        await ctx.send(temp_str)
        
    @commands.command()
    async def leave(self, ctx: Context):
        self.player_manager.leave_guild(ctx.guild.id)
        
    @commands.command()
    async def debug(self, ctx: Context):
        self.player_manager.print_players_DEBUG()

    @commands.command()
    async def chat(self, ctx: Context, *, message):
        pass

    @commands.command()
    async def recommend_movie(self, ctx: Context, *, keywords): 
        pass

async def setup(bot):
    await bot.add_cog(Music(bot))
    
