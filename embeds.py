from discord import Embed
from discord import Colour

def get_music_embed(track):
    music_embed = Embed(title='Playing ▶️', colour=Colour.random())
    music_embed.add_field(name=f'{track.title}', value='\u200b')
    music_embed.set_thumbnail(url=track.thumbnail)
    return music_embed

def get_queue_embed(keyword):
    queue_embed = Embed(title='Queued', colour=Colour.red())
    queue_embed.add_field(name=f'{keyword} added to the queue', value='\u200b')
    return queue_embed