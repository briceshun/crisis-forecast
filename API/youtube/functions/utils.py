# Clean up function
def cleanUp(data):
    output = []
    # Loop over all items in response
    keys = list(data['items'][0].keys())
    # Create dict if id not a dict
    try:
        for item in data['items']:
            dict = item[keys[0]] | item[keys[1]]
            output.append(dict)
    except TypeError:
        for item in data['items']:
            dict = {keys[0]: item[keys[0]]} | item[keys[1]]
            output.append(dict)
    return output