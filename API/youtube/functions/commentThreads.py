#%% API Client Library
import googleapiclient.discovery
from setup import *
from utils import *

#%% Youtube CommentThreads API Function
def youtubeCommentThreads(vidId):

    # API client
    youtube = googleapiclient.discovery.build(
                    api_service_name, 
                    api_version, 
                    developerKey = api_key
                    )

    # Individual video comment threads
    def videoCommentThreads(id):
        ## Default params
        fields='nextPageToken,items(id,snippet(topLevelComment(snippet(videoId,textDisplay,textOriginal,authorDisplayName,authorChannelId,likeCount,publishedAt,updatedAt))))'

        try:
            ### Initial reponse
            response = youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=id,
                    maxResults=100,
                    fields=fields
                    ).execute()
            
            ### Clean response
            output = cleanUp(response)

            ### Continue requests if more pages required
            while 'nextPageToken' in response.keys():
                #### API Response
                response = youtube.videos().list(
                    part="snippet,replies",
                    videoId=id,
                    maxResults=100,
                    fields=fields,
                    pageToken=response['nextPageToken']
                    ).execute()
                #### Clean response and add to data
                output += cleanUp(response)

            return output

        except:
            pass

    # Loop over videos in input list
    data = []
    for i in vidId:
        try:
            data += videoCommentThreads(i)
        except TypeError:
            pass
    
    return data
# %%
