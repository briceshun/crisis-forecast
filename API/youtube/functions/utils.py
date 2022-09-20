# Clean up function
def cleanUp(data):
    output = []
    keys = list(data['items'][0].keys())
    keys2 = list(data['items'][0][keys[1]].keys())

    # Check if CommentThreads API
    if len(keys2) == 1:
        ## CommentThreads API
        keys3 = list(data['items'][0]['snippet']['topLevelComment'].keys())
        ### Loop over all items in response
        for item in data['items']:
            #### Create variables to store data
            dict = item['snippet']['topLevelComment']
            #### Extract snippet dict to combine
            snippet = dict['snippet']
            #### Loop over all keys other than Snippet
            for i in keys3[1:]:
                snippet |= {i: dict[i]}
            #### Add replies
            try:
                snippet |= dict['replies']
            except:
                pass
            output.append(snippet)

    # Search and Videos API
    else:
        try:
            ## Loop over all items in response of Search API
            for item in data['items']:
                output.append(item[keys[0]] | item[keys[1]])
        except TypeError:
            ## Create dict for each item and append other dict for Videos API
            for item in data['items']:
                output.append({keys[0]: item[keys[0]]} | item[keys[1]])
    return output