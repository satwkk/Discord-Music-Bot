from hashlib import md5

cache = dict()
hash_format = '{}{}'

def hash_md5(inp):
    return md5(inp.encode()).hexdigest()
    
async def init_cache(bot):
    async for guild in bot.fetch_guilds():
        cache[guild.id] = list()

# Caches the track based on guild id and keyword inside a dictionary.
# TODO: Implement a multithreaded database connectivity to implement the caching and find a better key for hashing
def cache_track(func):
    async def wrapper(*args, **kwargs):
        ctx = args[1]
        keyword = args[2]
        hash = hash_md5(hash_format.format(ctx.guild.id, keyword))
        if hash in cache:
            print("found entry in cache, not extracting it again")
            return cache[hash]
        print('Not found entry in cache, extracting it')
        track = await func(*args, **kwargs)
        cache[hash] = track
        return track 
    return wrapper

# Class responsible for quering information from cache database
class CacheManager:
    def __init__(self):
        ...

    # Performs sql insert query
    def add_to_cache(self, data): ...
    # Performs sql select query
    def is_in_cache(self, data): ...
    # Performs sql delete query
    def remove_from_cache(self, data): ...