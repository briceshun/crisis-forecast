# %%
import asyncio
import pprint
from datetime import datetime as dt
from datetime import timedelta
from aiogoogle import Aiogoogle

# %%
api_key = 'AIzaSyAzdfQC7r04viSmZQy3mO0h3ytVpIziM3M'

async def ytSearch(
    query: str,
    key: str,
    results: int = 50,
    start: str = '1970-01-01',
    end: str = (dt.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
    fields: str = 'nextPageToken,items(id(videoId),snippet(publishedAt,channelId,channelTitle,title))'
    ):
    async with Aiogoogle(api_key=key) as aiogoogle:
        youtube = await aiogoogle.discover('youtube', 'v3')
        result = await aiogoogle.as_api_key(
            youtube.search.list(
            part='id,snippet',
            type='video',
            regionCode='US',
            order='relevance',
            q=query,
            maxResults=results,
            publishedAfter=start + 'T00:00:00Z',
            publishedBefore=end + 'T23:59:59Z',
            fields=fields
            )
        )
    return result

test = await ytSearch(query='test', key=api_key)

# %%
async def commentThreads(
    vidId: str,
    key: str = api_key,
    fields: str = 'nextPageToken,items(id,snippet(topLevelComment(snippet(videoId,textDisplay,textOriginal,authorDisplayName,authorChannelId,likeCount,publishedAt,updatedAt))))',
    pageToken: str = ''
    ):
    async with Aiogoogle(api_key=key) as aiogoogle:
        youtube = await aiogoogle.discover('youtube', 'v3')
        result = await aiogoogle.as_api_key(
            youtube.commentThreads.list(
                part="snippet,replies",
                videoId=vidId,
                maxResults=100,
                fields=fields,
                pageToken=pageToken
                )
        )
    return result

idx = ['3rZAQVJ9JKE', '-rbVOziCluY','KOyvVPc-HvU','rgQnkCWRh9o']
results = await asyncio.gather(*[commentThreads(i) for i in idx])
# %%
