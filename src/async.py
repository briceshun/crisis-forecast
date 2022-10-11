# %%
import asyncio
import json
from aiogoogle import Aiogoogle
from googleapiclient.errors import HttpError
from models import keys, quotaLimit

# %%
async def ytCommentThreads(
    vidId: str,
    key: str,
    fields: str = 'nextPageToken,items(id,snippet(topLevelComment(snippet(videoId,textDisplay,textOriginal,authorDisplayName,authorChannelId,likeCount,publishedAt,updatedAt))))',
    pageToken: str = ''
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

idx = ['3rZAQVJ9JKE', '-rbVOziCluY','KOyvVPc-HvU','rgQnkCWRh9o']
results1 = await asyncio.gather(*[ytCommentThreads(i) for i in idx])

# %%
async def ytCommentThreadsAll(
    vidId: str,
    key: keys,
    pageToken: str = ''
    ):
    result = []
    while True:
        try:
            response = await ytCommentThreads(vidId=vidId, key=key.active_key(), pageToken=pageToken)
            result += response['items']
        except HttpError as err:
            # Quota exceeded
            if 'disabled comments' in json.loads(err.content)['error']['errors'][0]['message']:
                break
            elif err.resp.status == 403:
                raise quotaLimit
            else:
                raise Exception('Unknown Error')
        if 'nextPageToken' not in response.keys():
            break

        pageToken = response['nextPageToken']

    return result

results = await asyncio.gather(*[ytCommentThreadsAll(i) for i in idx])
# %%
