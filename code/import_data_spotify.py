from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
import sys
import csv
import argparse

from cred_spotify import TOKENS

CLIENT_ID = TOKENS.CLIENT_ID
CLIENT_SECRET = TOKENS.CLIENT_SECRET

def parse_args():
    parser = argparse.ArgumentParser(description="Import Spotify data.")
    parser.add_argument("-n", "--name_artist", required=False, help="Name artist.")
    parser.add_argument("-e", "--export_data", required=False, help="File name export.")
    
    return parser.parse_args()

def get_artist(name, sp):
    results = sp.search(name)
    items = results['tracks']['items']
    if len(items) > 0:
        return items[0]['artists'][0]
    else:
        return None

def get_artist_id(artist, sp):
    return artist['id']

def get_artist_albums_id_names(id, sp):
  albums = sp.artist_albums(id, country = 'BR', limit=46)
  albums_id_name = {}
  for i in range(len(albums['items'])):
    id = albums['items'][i]['id']
    name = albums['items'][i]['name']
    albums_id_name[id] = name
 
  return albums_id_name

def get_album_songs(album_id, album_name, sp):
  spotify_album = {}
 
  tracks = sp.album_tracks(album_id)
  
  for n in range(len(tracks['items'])):
    id_track = tracks['items'][n]['id']
    track = sp.track(id_track)
    spotify_album[id_track] = {}
    
    spotify_album[id_track]['album'] = album_name
    spotify_album[id_track]['album_type'] = track['album']['album_type']
    spotify_album[id_track]['track_number'] = track['track_number']
    spotify_album[id_track]['id_track'] = track['id']
    spotify_album[id_track]['name'] = track['name']
    spotify_album[id_track]['popularity'] = track['popularity']
    spotify_album[id_track]['explicit'] = track['explicit']
    spotify_album[id_track]['duration_ms'] = track['duration_ms']
    spotify_album[id_track]['release_date'] = track['album']['release_date']
 
    artists_track = track['artists']
    spotify_album[id_track]['artists'] = []
    for artist in artists_track:
      spotify_album[id_track]['artists'].append(artist['name'])
  return spotify_album

def get_all_albums_songs(albums_ids_names, sp):
  spotify_albums = []
  albums_names = []
  for id, name in albums_ids_names.items():
    if name not in albums_names:
      albums_names.append(name)
      album_songs = get_album_songs(id,name, sp) 
    for item in album_songs.items():
      spotify_albums.append(item[1]) 
  return spotify_albums

def convert_to_csv(filepath, name):
  keys = filepath[0].keys()
  print(keys)
  csv_name = ''+ name + '.csv'
  with open(csv_name, 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(filepath)

def import_data():
    args = parse_args()
    sp = spotipy.Spotify(client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

    artist = get_artist(args.name_artist, sp)  
    
    if artist:
        artist_id = get_artist_id(artist, sp)
        albums_id_names = get_artist_albums_id_names(artist_id, sp)
        all_albums = get_all_albums_songs(albums_id_names, sp)
        convert_to_csv(all_albums, args.export_data)   
    else:
        logger.error("Can't find artist: %s", artist)
    

if __name__ == "__main__":
    import_data()