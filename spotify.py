import spotipy
from key import youtube_key
from googleapiclient.discovery import build
import re
from datetime import timedelta
import requests
import json
from key import spotify_app_client_secret_id, spotify_auth_token, spotify_client_id
from urllib.parse import urlencode
from youtube import playlist_name, videos_info, remove_words

class My_Spotify:
    def __init__(self):
        self.user_id = spotify_client_id
        self.user_secret_id = spotify_app_client_secret_id
        self.user_token = spotify_auth_token
        self.playlist_name = playlist_name
        self.index = None

    def token_header(self):
        headers = {
             "Content-Type": "application/json",
            "Authorization": f"Bearer {self.user_token}"
        }
        return headers

    def get_artist_id(self, artist, search_type, limit = 1):
        endpoint = "https://api.spotify.com/v1/search"
        headers = { "Authorization": f"Bearer {self.user_token}" }
        data = urlencode({"q": artist, "limit" : limit, "type" : search_type.lower()})
        base_url = f"{endpoint}?{data}"
        response = requests.get(base_url, headers = headers).json()
        if len(response["artists"]["items"]) == 0:
            return None
        return response["artists"]["items"][0]["id"]

    def get_user_id(self):
        base_url = "https://api.spotify.com/v1/me"
        response = requests.get(base_url, headers = self.token_header()).json()
        return response["id"]

    def playlist_exist(self):
        base_url = 	"https://api.spotify.com/v1/me/playlists"
        response = requests.get(base_url, headers = self.token_header()).json()
        playlist_id = ""
        playlist_present = 0
        for item in response["items"]:
            if item["name"] == playlist_name:
                playlist_present = 1
                playlist_id = item["id"]
        return {
            "playlist_present" : playlist_present,
            "playlist_id" : playlist_id
        }

    def creating_playlist(self):
        data = self.playlist_exist()
        if not data["playlist_present"]:
            user_id = self.get_user_id()
            query = f"https://api.spotify.com/v1/users/{user_id}/playlists"
            request_body = json.dumps({
                "name" : self.playlist_name,
                "description" : "spot you playlist",
                "public" : False
            })
            response = requests.post(query, data = request_body, headers = self.token_header()).json()
            return response["id"]
        else :
            return data["playlist_id"]

    def searching_the_album(self, artist_id):
        endpoint = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
        response = requests.get(endpoint,  headers = self.token_header()).json()
        album_id = []
        for item in response["items"]:
            album_id.append(item["id"])
        return self.search_the_song_in_album(album_id)

    def search_the_song_in_album(self, album_id):
        song_data = []
        for id_s in album_id:
            endpoint = f"https://api.spotify.com/v1/albums/{id_s}/tracks"
            response = requests.get(endpoint, headers = self.token_header()).json()
            for item in response["items"]:
                song_data.append({"name" : item["name"], "uri" : item["uri"]})
        return self.match_song(song_data)

    def match_song(self, song_data):
        for i in range(0, len(song_data)):
            song = song_data[i]["name"]
            size = len(song)
            index = 0
            data = []
            while index < size:
                k = ""
                while index < size and song[index].isalpha():
                    k += song[index];
                    index += 1
                if k != "":
                    if k.lower() not in remove_words:
                        data.append(k.lower())
                index += 1
            song_data[i]["name"] = data
        uri = None
        maxm = 0
        found_song = ""
        print(song_data)
        for artist_songs in song_data:
            artist_song = artist_songs["name"]
            song = videos_info[self.index]["song"]
            cnt = 0
            for i in range(0, len(song)):
                if i >= len(artist_song):
                    break
                if artist_song[i] == song[i]:
                    cnt += 1
                else :
                    break
            if cnt > 0 and cnt >= maxm:
                if cnt > maxm:
                    uri = artist_songs["uri"]
                    found_song = artist_songs["name"]
                else :
                    if len(song) < len(found_song):
                        uri = artist_songs["uri"]
                        found_song = artist_songs["name"]

                maxm = cnt
        return uri

    def search_song_from_videos_info(self):
        uris = []
        for i in range(0, len(videos_info)):
            self.index = i
            for artist in videos_info[i]["artist"]:
                artist_id = self.get_artist_id(artist, "artist")
                if artist_id != None:
                    uri_single = self.searching_the_album(artist_id)
                    if uri_single != None:
                        uris.append(uri_single)
                        break

        return uris;

    def add_song_to_playlist(self):
        playlist_id  = self.creating_playlist()
        uri_single_arr = self.search_song_from_videos_info()
        if len(uri_single_arr) > 0:
            endpoint = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
            request_body = json.dumps({
                "uris": uri_single_arr,
            })
            response = requests.post(endpoint, data = request_body,  headers = self.token_header()).json()


my_spotify = My_Spotify()
my_spotify.add_song_to_playlist()

