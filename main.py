import asyncio
import discord
import os

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
TOKEN = os.getenv("TOKEN")

cogs = ['music']

from player import players, MusicPlayer
class MrBeat(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix='-', intents=intents)

    async def on_ready(self):
        print(f'Bot Latency: {self.latency}')
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
