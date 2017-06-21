import os

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

DEVELOPER_KEY= os.environ.get('API_CODE')
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_by_keyword(search_key, max_results):
    youtube= build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    search_list=youtube.search().list(
        q=search_key,
        part="id,snippet",
        maxResults=max_results
    ).execute()
    
    videos=[]
    
    for search_result in search_list.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append("%s (%s)" % (search_result["snippet"]["title"],
                                 search_result["id"]["videoId"]))
                
    print ("Videos:\n", "\n".join(videos), "\n")
    
def channels_by_keyword(search_key, max_results):
    youtube= build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    search_list=youtube.search().list(
        q=search_key,
        part="id,snippet",
        maxResults=max_results,
        type='channel'
    ).execute()
    
    channels=[]
    
    for search_result in search_list.get("items", []):
        channels.append("%s (%s)" % (search_result["snippet"]["channelTitle"],
                                     search_result["snippet"]["channelId"]))
    
    print ("Channels:\n", "\n".join(channels), "\n")