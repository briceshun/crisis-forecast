"""
===================
UTILITIES
===================
User defined functions

- checkAPI      : Try API call and rotate keys if quota limit HTTP error raised
- cleanUp       : Extract data from response and reshape
- createIdStr   : Create list of concatenated ids (max 600 characters) for multiple api queries

"""

# %%
import json
from googleapiclient.errors import HttpError
from time import sleep
from models import noVideos, characterLimit, commentsDisabled

# %%
def checkAPI(key):
    def decorator(function):
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except HttpError as err:
                # Quota exceeded
                if 'disabled comments' in json.loads(err.content)['error']['errors'][0]['message']:
                    raise commentsDisabled
                elif err.resp.status == 403:
                    key.next_key()
                    return function(*args, **kwargs)
                # Server error - retry 2 more times
                elif err.resp.status in [500, 503]:
                    for i in range(0,2):
                        print(f"Retry: {i}")
                        sleep(5)
                        return wrapper(function(*args, **kwargs))
                # API length exceeds character limit
                elif err.resp.status == 400:
                    raise characterLimit
                # Others
                else:
                    raise Exception('Unknown Error')
        return wrapper
    return decorator

# %%
def cleanUp(data):
    output = []

    # Check if response is not null
    if len(data['items']) == 0:
        raise noVideos
    else:
        keys = list(data['items'][0].keys())
        keys2 = list(data['items'][0][keys[1]].keys())

        # Check if CommentThreads API
        if len(keys2) == 1:
            # CommentThreads API
            keys3 = list(data['items'][0]['snippet']['topLevelComment'].keys())
            # Loop over all items in response
            for item in data['items']:
                # Create variables to store data
                dict = item['snippet']['topLevelComment']
                # Extract snippet dict to combine
                snippet = dict['snippet']
                # Loop over all keys other than Snippet
                for i in keys3[1:]:
                    snippet |= {i: dict[i]}
                # Add replies
                try:
                    snippet |= dict['replies']
                except:
                    pass
                output.append(snippet)

        # Search and Videos API
        else:
            try:
                # Loop over all items in response of Search API
                for item in data['items']:
                    output.append(item[keys[0]] | item[keys[1]])
            except TypeError:
                # Create dict for each item and append other dict for Videos API
                for item in data['items']:
                    output.append({keys[0]: item[keys[0]]} | item[keys[1]])
        return output

# %%
def createIdStr(
    vidId: list,
    maxLen: int = 600
    ):
    output = []
    # Iterate over ids step by maxLen/concatLen + 1
    # where concatLen = 11 + 1 (id length + comma) 
    n = round(maxLen/12)
    for i in range(0, len(vidId), n):
        # If last id
        if i == len(vidId):
            output.append(vidId[i])
        # Last batch of ids
        elif i + n > len(vidId):
            output.append(','.join(vidId[i:]))
        # Concat normally for others
        else:
            output.append(','.join(vidId[i:i+n]))
    return output
# %%
