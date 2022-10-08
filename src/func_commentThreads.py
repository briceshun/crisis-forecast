"""
=============================
YOUTUBE API - COMMENT THREADS
=============================
User defined function to retrieve video comments and replies

Arguments
- vidId     : list of IDs to fetch data for
- key       : keys class

Optional:
- fields    : api response fields

Overview:   https://developers.google.com/youtube/v3/docs/commentThreads
List:       https://developers.google.com/youtube/v3/docs/commentThreads/list
Example:    https://github.com/youtube/api-samples/blob/master/python/commentThreads.py

"""

# %% Modules
import googleapiclient.discovery
from models import keys
from config import *
from utils import *

#%% Youtube CommentThreads API Function
def youtubeCommentThreads(
    vidId: str,
    key: keys,
    fields: str = 'nextPageToken,items(id,snippet(topLevelComment(snippet(videoId,textDisplay,textOriginal,authorDisplayName,authorChannelId,likeCount,publishedAt,updatedAt))))'
    ) -> list :

    # API functions

    @checkAPI(key)
    def ytCommentThreads(pageToken = ''):
        youtube = googleapiclient.discovery.build(
            api_service_name,
            api_version,
            developerKey=key.active_key()
        )

        response = youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=vidId,
                    maxResults=100,
                    fields=fields,
                    pageToken=pageToken
                    ).execute()
        return response

    try:
        # Initial Response
        response = ytCommentThreads()

        # Clean response
        data = cleanUp(response)
    except commentsDisabled:
        return [
            {'videoId': vidId,
            'textDisplay': 'Comments Disabled',
            'textOriginal': 'Comments Disabled',
            'authorDisplayName': 'N/A',
            'authorChannelId': {'value': 'N/A'},
            'likeCount': -1,
            'publishedAt': 'N/A',
            'updatedAt': 'N/A'
            }
        ]
    except noVideos:
        return [None]
    else:
        # Continue requests if more pages required
        while 'nextPageToken' in response.keys():
            # API Response
            response = ytCommentThreads(pageToken=response['nextPageToken'])
            # Clean response and add to data
            data += cleanUp(response)
    
    return data