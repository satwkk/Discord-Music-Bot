from extractors.spotify_player import SpotifyAlbumPlayer

items = SpotifyAlbumPlayer().extract_track('https://open.spotify.com/album/5H8mMbEO4YniyL71BPaOWR')

for i in items:
    print(i)
# for artist, song in items.items():
#     print(f'{artist}: {song}')