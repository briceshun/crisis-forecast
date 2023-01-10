"""
====================
YOUTUBE API - SEARCH
====================
User defined function to retrieve video data and id

Arguments
- query     : search term
- key       : keys class

Optional
- results   : no. of results per page
- start     : search start date
- end       : search end date
- pages     : no. of pages to retrieve
- fields    : api response fields

Overview:   https://developers.google.com/youtube/v3/docs/search
List:       https://developers.google.com/youtube/v3/docs/search/list
Example:    https://github.com/youtube/api-samples/blob/master/python/search.py

"""

# %%
# Modules
import googleapiclient.discovery
from datetime import datetime as dt
from datetime import timedelta
import models
from config import *
from utils import *

# %%
# %% Youtube Search API Function
def youtubeSearch(query: str,
                key: models.keys,
                results: int = 50,
                start: str = '1970-01-01',
                end: str = (dt.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
                pages: int = 1,
                fields: str = 'nextPageToken,items(id(videoId),snippet(publishedAt,channelId,channelTitle,title))'
                ):

    # API functions
    @checkAPI(key)
    def ytSearch(pageToken=''):
        youtube = googleapiclient.discovery.build(
            api_service_name,
            api_version,
            developerKey=key.active_key()
        )

        response = youtube.search().list(
            part='id,snippet',
            type='video',
            regionCode='US',
            order='relevance',
            q=query,
            maxResults=results,
            publishedAfter=start + 'T00:00:00Z',
            publishedBefore=end + 'T23:59:59Z',
            fields=fields,
            pageToken=pageToken
            ).execute()
        return response

    # Initial reponse
    response = ytSearch()

    # If function does not return None
    if response:
        # Clean response
        data = cleanUp(response)

        # Continue requests if more pages required
        if pages > 1:
            # Intialise counter
            counter = 1
            # Loop until all pages fetched
            while counter < pages:
                # API Response
                response = ytSearch(pageToken=response['nextPageToken'])
                if response:
                    # Clean response and add to data
                    data += cleanUp(response)
                    # Increment counter
                    counter += 1
                else:
                    break

        # Extract video ids
        ids = [v['videoId'] for v in data]

        return data, ids
        
    else:
        raise noVideos