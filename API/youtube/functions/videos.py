#%% API Client Library
import googleapiclient.discovery
from functions.setup import *
from functions.utils import *

#%% Youtube Videos API Function
def youtubeVideos(vidId):

    # API client
    youtube = googleapiclient.discovery.build(
                    api_service_name, 
                    api_version, 
                    developerKey = api_key
                    )

    # Default params
    fields = 'nextPageToken, items(id, statistics)'

    # Initial reponse
    response = youtube.videos().list(
            part="statistics,contentDetails",
            id=','.join(vidId),
            maxResults=100,
            fields=fields
            ).execute()

    # Clean response
    data = cleanUp(response)

    # Continue requests if more pages required
    while 'nextPageToken' in response.keys():
        # API Response
        response = youtube.videos().list(
            part="statistics,contentDetails",
            id=','.join(vidId),
            maxResults=100,
            fields=fields,
            pageToken =  response['nextPageToken']
            ).execute()
        # Clean response and add to data
        data += cleanUp(response)

    return data
# %%
