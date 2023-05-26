import os
import asyncio
import discord
from discord.ext.commands import errors
from discord.ext.commands.context import Context
from discord.message import Message

from dotenv import load_dotenv
from discord.ext import commands
from song_queue import init_queue
from cache import init_cache

load_dotenv()
TOKEN = os.getenv("TOKEN")

cogs = ['music']

class MrBeat(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix='-', intents=intents)

    async def on_ready(self):
        # Initializing global systems on ready
        await init_queue(self)
        await init_cache(self)
        print("Bot ready ... ")

    async def on_command_error(self, context, exception):
        print(context.message)
        print(str(exception))

async def main():
    bot = MrBeat()
    for cog in cogs:
        await bot.load_extension(cog)
    await bot.start(TOKEN)
    
asyncio.run(main())
