import os
import datetime as datetime
import pytz
import pandas as pd
import csv
import json
import time

from retrying import retry
from retrying import RetryError
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

DEVELOPER_KEY= os.environ.get('API_CODE')
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
service= build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

def channel_date_keyword(searchKey,pageToken,dt,dt2):
    search_list=service.search().list(
        q=searchKey,
        part="id,snippet",
        maxResults=50,
        order="relevance",
        type="channel",
        publishedAfter=dt,
        publishedBefore=dt2,
        pageToken=pageToken
    ).execute()
    
    return search_list

@retry(stop_max_attempt_number=7,retry_on_exception=is_503_error, 
       wrap_exception=True,wait_random_min=1000, wait_random_max=2000)
def channel_by_id(search_id):
    channels=service.channels().list(
        id=search_id,
        part="id, snippet, brandingSettings, contentDetails, invideoPromotion, statistics, topicDetails",
        maxResults=50
    ).execute()
    return channels

# get basic channel list with ids (years defined)
def get_channel_list(year,yearParts,day,searchKey,fileName,fileName2,prevQuota):
    newQuota=prevQuota
    
    for x in range (1,yearParts+1):
        pageToken=""
        d=datetime.datetime(year,int(1+(12/yearParts)*(x-1)),1,0,0).isoformat()+'Z'
        d2=datetime.datetime(year,int((12/yearParts)*x),day[x-1],0,0).isoformat()+'Z'
       
        while(pageToken!='CLYHEAA'):
            channelList=channel_date_keyword(searchKey,pageToken,d,d2)
            newQuota+=100
            
            #save list and channels if list is not empty
            if (channelList.get("items",[])!=[]):
                
                #save json dict Channel List 50 items
                with open(fileName,'a')as fp1:
                    out1=json.dumps(channelList)
                    fp1.write(out1 + '\n')
            
                #save the data about the channels in the list
                for channel in channelList.get("items", []):
                    try:
                        channelData=channel_by_id(channel["id"]["channelId"])
                    except RetryError as e:
                        print("max unsuccessful attempts reached"+" id:"+channel["id"]["channelId"])
                        continue
                    newQuota+=15
                    with open(fileName2,'a')as fp2:
                        out2=json.dumps(channelData)
                        fp2.write(out2 + '\n')
                    time.sleep(1)
                    
            pageToken=channelList["nextPageToken"]
            time.sleep(1)
            
        time.sleep(1)
        
    return newQuota

# get trimestral info for 10 years of channels related to search keys
#year=2007
yearParts=3
day=[30,31,31]
#searchKeys=["minecraft","roblox","call of duty","overwatch"]
#fileNames=['minecraft_ch_list.json','roblox_ch_list.json','callOD_ch_list.json','overwatch_ch_list.json']
#fileNames2=['minecraft_ch_data.json','roblox_ch_data.json','callOD_ch_data.json','overwatch_ch_data.json']
searchKeys=["grand theft auto","league of legends","Happy wheels","five nights at freddy's","agar.io", "pokemon go"]
fileNames=['gta_list.json','LOL_list.json','happyW_list.json','fivenaf_list.json','agario_list.json','pkgo_list.json']
fileNames2=['gta_data.json','LOL_data.json','happyW_data.json','fivenaf_data.json','agario_data.json','pkgo_data.json']
prevQuota=510

for i in range (3,4):
    for year in range (2007,2018):
        quota=get_channel_list(year,yearParts,day,searchKeys[i],fileNames[i],fileNames2[i],prevQuota)
        prevQuota=quota
        print (prevQuota)
        time.sleep(10)

def is_503_error(exception):
    is503=False
    if (isinstance(exception, HttpError)):
        if (exception.resp.status==503):
            is503=True
    return (is503)


