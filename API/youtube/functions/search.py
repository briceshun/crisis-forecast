# %% API Client Library
import googleapiclient.discovery
from datetime import datetime as dt
from datetime import timedelta
from classes.api_key import *
from functions.setup import *
from functions.utils import *

# %% Youtube Search API Function
def youtubeSearch(query,
                key,
                results=50,
                start='1970-01-01',
                end=(dt.today() + timedelta(days=1)).strftime('%Y-%m-%d'),
                pages=1,
                fields = 'nextPageToken,items(id(videoId),snippet(publishedAt,channelId,channelTitle,title))'
                ):

    # API functions
    @check_key(key)
    def youtube_search(pageToken=''):
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
    response = youtube_search()

    # If function returns None
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
                response = youtube_search(pageToken=response['nextPageToken'])
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
        return None, None