import os
import utils
import spotipy as sp

from dotenv import load_dotenv
from extractors.base_player import Player
from extractors.default_player import DefaultPlayer

load_dotenv()

# Initializing spotify client
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

auth_manager = sp.SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
sp_client = sp.Spotify(auth_manager=auth_manager)

class SpotifyTrackPlayer(Player):
    def __init__(self): 
        super().__init__()
        
    def get_track_details(self, track):
        song, author = track['name'], ', '.join(artist['name'].encode('ascii', 'ignore').decode('latin-1') for artist in track['artists'])
        return (song, author)
    
    async def extract_track(self, url):
        # TEST URL: https://open.spotify.com/track/2ksyzVfU0WJoBpu8otr4pz
        id = utils.get_id(url)
        track = sp_client.track(id)
        
        if not track: 
            return None
        
        song, author = self.get_track_details(track)
        track = await DefaultPlayer().extract_track(f'{song} - {author}')
        return track
        
class SpotifyPlaylistPlayer(Player):
    def __init__(self):
        super().__init__()
        
    def get_playlist_items(self, playlist):
        items = dict()
        
        for item in playlist['items']:
            track = item['track']
            
            if not track: return None
            
            song, artist = track['name'], \
            ', '.join(artist['name']
                .encode('ascii', 'ignore')
                .decode('latin-1') 
                for artist in track['artists'])
            items[artist] = song
            
        return items
        
    async def extract_track(self, url):
        playlist = sp_client.playlist_items(utils.get_id(url))
        playlist_items = self.get_playlist_items(playlist)
        return playlist_items
        
# TODO:
class SpotifyAlbumPlayer(Player):
    def __init__(self):
        super().__init__()