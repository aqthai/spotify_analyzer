'''
    Author: Alvin Thai
    Per Scholas Capstone I 
    Recommender connects with the spotify API to produce songs recommendations based 
    on the input playlist.  Entering a playlist URL will load all songs into a 
    dictionary.  Clicking the shuffle button picks five songs at random 
    from the dictionary.  Clicking the recommend button will call the Spotify
    API to recommend five songs and display them on the GUI.  
'''

import requests
import json
import base64
from pprint import pprint
from dotenv import dotenv_values
import random
import tkinter as tk
from tkinter import ttk
import re

# Global variables
s_links = {}
random_songs = []
radio_group = []
headers = {}
data = {}

def connect_api(config, TOKEN_URL):
    '''
    Reads client id, client secret, and token url to modify global variables
    that connect to Spotify API
    '''
    global headers
    global data
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

    # Default playlist is Vangelis
    playlistId = "37i9dQZF1E4DxWTWjR3190"
    playlistUrl = f"https://api.spotify.com/v1/playlists/{playlistId}"

    headers = {
        "Authorization" : "Bearer " + token
    }

    res = requests.get(url=playlistUrl, headers=headers)
    p_dict = json.loads(json.dumps(res.json(), indent=2))

    # makes list of (track_name, artist, track_id, artist_id) tuples
    names_artist = [(item['track']['name'], item['track']['album']['artists'][0]['name'],
        item['track']['id'], item['track']['album']['artists'][0]['id'])
        for item in p_dict['tracks']['items']]

    # make a dictionary of artist name keys to artist id, track name, and track id tuples
    global s_links
    for song in names_artist:
        s_links[(song[1], song[3])] = s_links.get((song[1], song[3]), []) + [(song[0], song[2])]

# build GUI
window = tk.Tk()
window.title('Song Recommender')
frm_a = ttk.Frame()
frm_b = ttk.Frame()

lbl_a = tk.Label(
    master=frm_a,
    text="Song Recommender",
    fg="white",
    bg="black",
    width=25,
    height=5
)
lbl_a.pack()

ent_playlist = tk.Entry(
    master=frm_a,
    fg="yellow",
    bg="blue",
    width=50
)

def playlist_click(event):
    '''
    Process the link provided in entry for playlist ID to recreate s_link dictionary
    '''
    playlistUrl=ent_playlist.get()
    ent_playlist.delete(0, tk.END)
    pattern = r'.*playlist\/(\w*)'
    playlistId = re.search(pattern, playlistUrl).group(1)
    playlistUrl = f"https://api.spotify.com/v1/playlists/{playlistId}"
    res = requests.get(url=playlistUrl, headers=headers)
    p_dict = json.loads(json.dumps(res.json(), indent=2))

    lbl_a['text'] = p_dict['name'] + " playlist"
    print(p_dict['name'] + " playlist")

    names_artist = [(item['track']['name'], item['track']['album']['artists'][0]['name'],
        item['track']['id'], item['track']['album']['artists'][0]['id'])
        for item in p_dict['tracks']['items']]

    # make a dictionary of artist name keys to artist id, track name, and track id tuples
    s_links.clear()
    for song in names_artist:
        s_links[(song[1], song[3])] = s_links.get((song[1], song[3]), []) + [(song[0], song[2])]
    for k, v in s_links.items():
        print(k, v)

btn_playlist = tk.Button(
    master=frm_a,
    text="Read playlist",
    width=25,
    height=5,
    bg="blue",
    fg="yellow"
)
btn_playlist.bind("<Button-1>", playlist_click)

def shuffle_click(event):
    '''
    Reassign radio buttons to show random tracks from s_links dictionary. 
    '''
    for r in radio_group:
        r.pack_forget()
    random_songs.clear()
    while len(random_songs) < 5:
        random_artist = random.choice(list(s_links))
        song = random.choice(s_links[random_artist])
        if not (random_artist, song) in random_songs:
            random_songs.append((random_artist, song)) 

    for random_artist, song in random_songs:
        r = ttk.Radiobutton(
            window,
            text = song[0] + " by " + random_artist[0],
            value = (song[1], random_artist[1]),
            variable = selected_song
        )
        radio_group.append(r)
        r.pack(fill='x', padx=5, pady=5)

btn_shuffle = tk.Button(
    master=frm_b,
    text="Shuffle",
    width=25,
    height=5,
    bg="blue",
    fg="yellow"
)
btn_shuffle.bind("<Button-1>", shuffle_click)

lbl_b = tk.Label(
    master=frm_b,
    text="Recommendations",
    fg="white",
    bg="black",
    width=60,
    height=20
)
lbl_b.pack(fill=tk.BOTH, expand=True)

def rec_click(event):
    '''
    Call Spotify to recommend songs and display them in frame 2.
    '''
    artist = selected_song.get().split()[1]
    song = selected_song.get().split()[0]
    res = requests.get('https://api.spotify.com/v1/recommendations?limit=5&market=ES&seed_artists='
    + artist + '&seed_genres=''&seed_tracks=' + song, headers=headers)
    recommendations = json.loads(json.dumps(res.json(), indent=2))
    lbl_b['text'] = "Recommendations: \n"
    for item in recommendations['tracks']:
        print(item['name'], item['external_urls']['spotify'])
        lbl_b['text'] += "\n" + item['name'] + " by " + str([person['name'] for person in item['artists']]) + "\n"

btn_rec = tk.Button(
    master=frm_b,
    text="Recommend",
    width=25,
    height=5,
    bg="blue",
    fg="yellow"
)
btn_rec.bind("<Button-1>", rec_click)

# Pack widgets onto GUI
frm_a.pack(fill=tk.BOTH, expand=True)
ent_playlist.pack()
ent_playlist.insert(0, "Playlist link here")
btn_playlist.pack(fill=tk.BOTH, expand=True)
frm_b.pack(fill=tk.BOTH, expand=True)
btn_rec.pack(fill=tk.BOTH, expand=True)
btn_shuffle.pack(fill=tk.BOTH, expand=True)

def main():
    config = dotenv_values('.env')
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    connect_api(config, TOKEN_URL)

if __name__ == '__main__':
    main()

# Recommends random songs from playlist at the end of frame b
selected_song = tk.StringVar()
while len(random_songs) < 5:
    random_artist = random.choice(list(s_links))
    song = random.choice(s_links[random_artist])
    if not (random_artist, song) in random_songs:
        random_songs.append((random_artist, song)) 

for random_artist, song in random_songs:
    r = ttk.Radiobutton(
        window,
        text = song[0] + " by " + random_artist[0],
        value = (song[1], random_artist[1]),
        variable = selected_song
    )
    radio_group.append(r)
    r.pack(fill='x', padx=5, pady=5)

window.mainloop()