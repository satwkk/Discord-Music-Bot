from typing import Union

global_queue = dict()

async def init_queue(bot):
    async for guild in bot.fetch_guilds():
        global_queue[guild.id] = list()

def get_guild_queue(guild_id):
    return global_queue[guild_id] 

def enqueue_song(guild_id, item: Union[str, dict[str, str]]):
    queue = get_guild_queue(guild_id)
    if isinstance(item, str): 
        queue.append(item)
    else:
        for song, author in item.items():
            queue.append(f'{song} - {author}')

def dequeue_song(guild_id):
    queue = get_guild_queue(guild_id)
    return queue.pop(0)

def clear_queue(guild_id):
    get_guild_queue(guild_id).clear()