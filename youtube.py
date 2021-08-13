from key import youtube_key, url
from googleapiclient.discovery import build
import urllib.parse as urlparse
from urllib.parse import parse_qs
import json

videos_info = []
playlist_name = None
remove_words = []

class My_Youtube:
    def __init__(self):
        self.youtube = build("youtube", "v3", developerKey = youtube_key)
        self.playlist_id = self.get_playlist_id()

    def get_playlist_id(self):
        parsed = urlparse.urlparse(url)
        return parse_qs(parsed.query)['list'][0]

    def get_playlist_name(self):
        playlist_request = self.youtube.playlists().list(
            part = "contentDetails, snippet",
            id = self.playlist_id
        )
        playlist_response = playlist_request.execute()
        return playlist_response["items"][0]['snippet']['title']

    def get_videos_info_from_playlist(self):
        next_page_token = None
        while True:
            pl_item_request = self.youtube.playlistItems().list(
                part = "contentDetails, id",
                playlistId = self.playlist_id,
                maxResults = 50,
                pageToken = next_page_token
            )
            pl_item_response = pl_item_request.execute()
            videos_id = []
            for item in pl_item_response['items']:
                vid_id = item["contentDetails"]["videoId"]
                videos_id.append(vid_id)
            video_request  = self.youtube.videos().list(
                part = "contentDetails, snippet",
                id =  ','.join(videos_id),
            )
            video_response = video_request.execute()
            video_desc = []
            for item in video_response["items"]:
                video_desc.append({
                    "title": item["snippet"]["title"],
                    "channelTitle":  item["snippet"]["channelTitle"]
                })
            next_page_token = pl_item_response.get("nextPageToken")
            if not next_page_token:
                break
        return self.get_artist_and_song(video_desc)

    def get_artist_and_song(self, video_desc):
        for video in video_desc:
            title = video["title"]
            channelTitle = video["channelTitle"]
            artist = []
            songs = []
            st = 0
            size = len(title)
            for i in range(0, size):
                if title[i] == '-':
                    st = i + 1;
                    x = title[0: i - 1]
                    artist.append(x)
                    break
            if len(artist) > 0:
                if channelTitle != artist[0]:
                    artist.append(channelTitle)    
            else :
                artist.append(channelTitle) 
            song = []
            index = st
            while index < size:
                k = ""
                while index < size and title[index].isalpha():
                    k += title[index];
                    index += 1
                if k != "":
                    if k.lower() not in remove_words:
                        song.append(k.lower())
                index += 1
            videos_info.append({
                "artist" : artist,
                "song" : song
            })

my_youtube = My_Youtube()
my_youtube.get_videos_info_from_playlist()
playlist_name = my_youtube.get_playlist_name()

print(videos_info)
