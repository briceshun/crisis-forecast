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
import asyncio
import json
from aiogoogle import Aiogoogle
from googleapiclient.errors import HttpError
from models import keys, quotaLimit

#%% Youtube CommentThreads API Function
# Initial Response
async def ytCommentThreads(
    vidId: str,
    key: str,
    fields: str,
    pageToken: str
    ):
    async with Aiogoogle(api_key=key) as aiogoogle:
        youtube = await aiogoogle.discover('youtube', 'v3')
        response = await aiogoogle.as_api_key(
            youtube.commentThreads.list(
                part="snippet,replies",
                videoId=vidId,
                maxResults=100,
                fields=fields,
                pageToken=pageToken
                )
        )

    return response

# Pagination Loop
async def youtubeCommentThreads(
    vidId: str,
    key: keys,
    fields: str = 'nextPageToken,items(id,snippet(topLevelComment(snippet(videoId,textDisplay,textOriginal,authorDisplayName,authorChannelId,likeCount,publishedAt,updatedAt))))',
    pageToken: str = ''
    ):
    result = []
    counter = 1
    while True:
        try:
            response = await ytCommentThreads(vidId=vidId, key=key.active_key(), fields=fields, pageToken=pageToken)
            result += response['items']
            counter += 1
        except:
            break
        if 'nextPageToken' not in response.keys():
            break
        if counter >= 10:
            break

        pageToken = response['nextPageToken']

    return result