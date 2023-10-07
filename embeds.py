from discord import Embed
from discord import Colour

def get_music_embed(track):
    music_embed = Embed(title='Playing ▶️', colour=Colour.random())
    music_embed.add_field(name=f'{track.title}', value='\u200b')
    music_embed.set_thumbnail(url=track.thumbnail)
    return music_embed

def get_queue_embed(keyword):
    queue_embed = Embed(title=f'{keyword} added to the queue', colour=Colour.red())
    return queue_embed

def get_update_embed():
    update_embed = Embed(title='**NEW FEATURES**', colour=Colour.yellow())
    update_embed.add_field(name='Repeat', value='Now you can repeat the currently playing song using the -repeat command')
    return update_embed
