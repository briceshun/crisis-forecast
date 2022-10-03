from googleapiclient.errors import HttpError
from time import sleep
from classes.exceptions import *

# Check API keys function
def check_key(key):
    def decorator(function):
        def wrapper(apikey = key):
            try:
                return function()
            except HttpError as err:
                # Quota exceeded
                if err.resp.status == 403:
                    apikey.next_key()
                    return function()
                # Server error
                elif err.resp.status in [500, 503]:
                    sleep(5)
                    return function()
                # Others
                else:
                    return None
        return wrapper
    return decorator

# Clean up function
def cleanUp(data):
    output = []

    # Check if response is not null
    if len(data['items']) == 0:
        raise NoVideosError
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