import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import requests
from dotenv import dotenv_values
import json
import base64
from pprint import pprint
import random

config = dotenv_values('.env')

AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
base_url = 'https://api.spotify.com/v1/'


# auth_code = requests.get(AUTH_URL, {
#     'client_id': config['client_id'],
#     'response_type': 'code',
#     'redirect_uri': 'http://127.0.0.1:9090'
# })  
# print(auth_code)

# Authorization, done once
# token_code = requests.post(TOKEN_URL, {
#     'grant_type' : 'authorization_code',
#     'code' : auth_code,
#     'redirect_uri' : 'http://127.0.0.1:9090'
# })
# print(token_code)

# auth_response = requests.post(TOKEN_URL, {
#     'grant_type' : 'client_credentials',
#     'client_id' : config['client_id'],
#     'client_secret' : config['client_secret']
# })

# auth_response_data = auth_response.json()
# accesstoken = auth_response_data['access_token']

headers = {}
data = {}

# Encode as Base64
message = f"{config['client_id']}:{config['client_secret']}"
messageBytes = message.encode('ascii')
base64Bytes = base64.b64encode(messageBytes)
base64Message = base64Bytes.decode('ascii')

# define fields for request get 
headers['Authorization'] = f"Basic {base64Message}"
data['grant_type'] = "client_credentials"

r = requests.post(TOKEN_URL, headers=headers, data=data)
token = r.json()['access_token']

playlistId = "37i9dQZF1E4DxWTWjR3190"
playlistUrl = f"https://api.spotify.com/v1/playlists/{playlistId}"

headers = {
    "Authorization" : "Bearer " + token
}

res = requests.get(url=playlistUrl, headers=headers)
p_dict = json.loads(json.dumps(res.json(), indent=2))

print(p_dict['name'] + " playlist")


names_artist = [(item['track']['name'], item['track']['album']['artists'][0]['name'],
    item['track']['id'], item['track']['album']['artists'][0]['id'])
     for item in p_dict['tracks']['items']]

# make a dictionary of artist name keys to artist id, track name, and track id tuples
s_links = {}
for song in names_artist:
    s_links[(song[1], song[3])] = s_links.get((song[1], song[3]), []) + [(song[0], song[2])]
print(s_links)

artist = input('artist id: ')
genre = input('genre: ')
track = input('track id: ')
res = requests.get('https://api.spotify.com/v1/recommendations?limit=5&market=ES&seed_artists=' + artist + '&seed_genres=' + genre + '&seed_tracks=' + track, headers=headers)
recommendations = json.loads(json.dumps(res.json(), indent=2))

pprint(recommendations['tracks'])
for item in recommendations['tracks']:
    print(item['album']['name'], item['album']['external_urls'])
