from key import youtube_key
from googleapiclient.discovery import build
import re
from datetime import timedelta

youtube = build("youtube", "v3", developerKey=youtube_key)

'''query for channel'''
# ch_request = youtube.channels().list(
#     part="contentDetails, statistics",
#     forUsername = 'schafer5',
# )
#
# ch_response = ch_request.execute()

''''query for playlists'''
# pl_request = youtube.playlists().list(
#     part="contentDetails, snippet",
#     channelId= "UCCezIgC97PvUuR4_gbFUs5g"
# )
# pl_response = pl_request.execute()
# print(pl_response)
# for item in pl_response['items']:
#     print(item)
#     print()


minutes_pattern = re.compile(r'(\d+)M')
seconds_pattern = re.compile(r'(\d+)S')
hours_pattern = re.compile(r'(\d+)H')

playlist_id = "OLAK5uy_lIh621OMo4dgezJVXJ1d_zVHeClb6RYRU"

total_seconds = 0
next_page_token = None
while True:
    ''''query for playlist items'''
    pl_item_request = youtube.playlistItems().list(
        part = "contentDetails",
        playlistId = playlist_id,
        maxResults = 50,
        pageToken = next_page_token
    )
    pl_item_response = pl_item_request.execute()
    vid_ids = []
    for item in pl_item_response['items']:
        video_id = item['contentDetails']['videoId']
        vid_ids.append(video_id)

    #print(','.join(vid_ids))

    vid_request = youtube.videos().list(
        part = "contentDetails",
        id = ','.join(vid_ids)
    )
    vid_response = vid_request.execute()
    for item in vid_response['items']:
        duration = item['contentDetails']['duration']
        #print(duration)
        hours = hours_pattern.search(duration)
        minutes = minutes_pattern.search(duration)
        seconds = seconds_pattern.search(duration)
        #print(hours, minutes, seconds)
        minutes = int(minutes.group(1)) if minutes else 0
        seconds = int(seconds.group(1)) if seconds else 0
        hours = int(hours.group(1)) if hours else 0
        #print(minutes,seconds, hours)
        video_seconds = timedelta(
            hours = hours,
            minutes = minutes,
            seconds = seconds
        ).total_seconds()
        total_seconds += video_seconds
    next_page_token = pl_item_response.get('nextPageToken')
    if not next_page_token:
        break

#print(total_seconds)
hours = int(total_seconds / 3600)
minutes = int((total_seconds - hours * 3600) / 60)
seconds = int(total_seconds - hours * 3600 - minutes * 60)
print(f'{hours}:{minutes}:{seconds}')