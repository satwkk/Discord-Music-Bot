from typing import Union

global_queue = dict()

def init_queue(guilds_ids):
    for guild_id in guilds_ids:
        global_queue[guild_id] = list()

def get_guild_queue(guild_id):
    return global_queue[guild_id] 

def add_to_queue(guild_id, item: Union[str, dict[str, str]]):
    queue = get_guild_queue(guild_id)
    if isinstance(item, str): 
        queue[guild_id].append(item)
    else:
        for song, author in item.items():
            queue[guild_id].append(f'{song} - {author}')

def enqueue_song(guild_id):
    queue = get_guild_queue(guild_id)
    return queue.pop(0)

def clear_queue(guild_id):
    get_guild_queue(guild_id).clear()