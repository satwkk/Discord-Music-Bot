from hashlib import md5

cache = dict()
hash_format = '{}{}'

def hash_md5(inp):
    return md5(inp.encode()).hexdigest()
    
# Caches the track based on guild id and keyword inside a dictionary.
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

