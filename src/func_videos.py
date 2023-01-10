"""
====================
YOUTUBE API - VIDEOS
====================
User defined function to retrieve video stats

Arguments
- vidId     : list of IDs to fetch data for
- key       : keys class

Optional:
- fields    : api response fields

Overview:   https://developers.google.com/youtube/v3/docs/videos
List:       https://developers.google.com/youtube/v3/docs/videos/list
Example:    https://github.com/youtube/api-samples/blob/master/python/videos.py

"""

# %% Modules
import googleapiclient.discovery
from models import keys
from config import *
from utils import *

#%% Youtube Videos API Function
def youtubeVideos(
    vidIdStr: str, 
    key: keys,
    fields: str = 'nextPageToken, items(id, statistics)'
    ) -> list :

    # API functions
    @checkAPI(key)
    def ytVideos(pageToken=''):
        youtube = googleapiclient.discovery.build(
            api_service_name,
            api_version,
            developerKey=key.active_key()
        )

        response = youtube.videos().list(
            part="statistics,contentDetails",
            id=vidIdStr,
            maxResults=100,
            fields=fields,
            pageToken=pageToken
            ).execute()
        return response

    # Initial reponse
    response = ytVideos()

    # Clean response
    data = cleanUp(response)

    # Continue requests if more pages required
    while 'nextPageToken' in response.keys():
        # API Response
        response = ytVideos(pageToken=response['nextPageToken'])
        # Clean response and add to data
        data += cleanUp(response)

    return data