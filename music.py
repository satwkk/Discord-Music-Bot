from db import handle
from typing import List
from dotenv import load_dotenv
from discord.ext import commands
from embeds import get_queue_embed
from models.pollanswer import Answer
from player import MusicPlayerManager
from player import players, MusicPlayer
from discord.ext.commands import Bot, Context
from discord import Member, Poll, PollAnswer, PollMedia, Message, VoiceChannel

import datetime
import math
import os

load_dotenv()
DEV_ID = int(os.getenv('DEV_ID'))

def validate_command_invoker(ctx: Context):
    return ctx.author.voice.channel is not None

def admin_callable(ctx: Context):
    return ctx.message.author.id == DEV_ID or ctx.message.author.id == ctx.guild.owner_id

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
        if not self.player_manager.is_guild_player_registered(ctx.guild.id):
            self.player_manager.register_guild_player(ctx.guild.id, MusicPlayer(self.bot))

        self.player_manager.get_guild_player(ctx.guild.id) \
            .add_track(ctx, keyword)

    @commands.command()
    async def save(self, ctx: Context) -> None:
        serialized_obj = self.player_manager.get_current_song(ctx.guild.id).get_serialized_format()
        handle.cursor() \
            .execute(
                f'INSERT INTO {ctx.guild.id} VALUES ()'
            )
        handle.commit()

    @commands.command()
    async def skip(self, ctx: Context):
        if len(self.player_manager.get_guild_queue(ctx.guild.id)) == 0:
            await ctx.send('No messages in queue')
            return

        media = PollMedia(text="Do you want to skip the current song")
        poll = Poll(media, duration=datetime.timedelta(hours=1))
        poll.add_answer(text="Yes👍")
        poll.add_answer(text="No 👎")
        await ctx.send(poll=poll)

    @commands.command()
    @commands.check(admin_callable)
    async def skip_admin(self, ctx: Context):
        self.player_manager.skip_guild_track(ctx.guild.id)

    @commands.Cog.listener()
    async def on_poll_vote_add(self, user: Member, answer: PollAnswer):
        try:
            n = len(user.voice.channel.members)
            n = math.ceil(n/2)

            # If the number of votes are greater than half of users
            if answer.poll.total_votes == n:
                await answer.poll.end()

                answers: List[PollAnswer] = answer.poll.answers

                yes = answers[0]
                no = answers[1]
                # default_answer = no

                if yes.vote_count > no.vote_count:
                    self.player_manager.skip_guild_track(user.guild.id)
                else:
                    await answer.poll.message.channel.send("Cannot skip the track.")
        except Exception as e:
            print(str(e))

    @commands.Cog.listener()
    async def on_poll_vote_remove(self, user: Member, answer: PollAnswer): ...
    
    @commands.command()
    async def pause(self, ctx: Context):
        self.player_manager.pause_guild_track(ctx.guild.id)
    
    @commands.command()
    async def resume(self, ctx: Context):
        self.player_manager.resume_guild_track(ctx.guild.id)
        
    @commands.command()
    async def repeat(self, ctx: Context) -> None:
        if self.player_manager.register_repeat_request(ctx.guild.id): 
            await ctx.send('Repeat request has been queued.')
        else: 
            await ctx.send('Play a song to send repeat request.')

    @commands.command()
    async def reset(self, ctx: Context) -> None:
        self.player_manager.reset_guild_player(ctx.guild.id)
            
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
        print(self.player_manager.get_guild_queue(ctx.guild.id))
        self.player_manager.print_players_DEBUG()

async def setup(bot):
    await bot.add_cog(Music(bot))
    
