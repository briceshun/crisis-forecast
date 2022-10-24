"""
================
EVENT - GAMESTOP
================



"""

# %%
import asyncio
import json
from datetime import datetime, timedelta
from time import sleep
from func_search import youtubeSearch
from func_videos import youtubeVideos
from func_commentThreads import youtubeCommentThreads
from models import keys, noVideos
from models.exceptions import quotaLimit
from utils import createIdStr, commentProcess

# %% Date Range
startdate = datetime.strptime('2020-12-01', '%Y-%m-%d')
enddate = datetime.strptime('2021-06-30', '%Y-%m-%d')

dates = []
dates1 = []

while startdate <= enddate:
    dates.append(startdate.strftime('%Y-%m-%d'))
    dates1.append((startdate + timedelta(days=1)).strftime('%Y-%m-%d'))
    startdate += timedelta(days=1)

# %% Get Videos
key = keys()
videos, ids, date = [], [], []
counter = 1
for i, j in zip (dates, dates1):
    print(f"%s - Fetching top 50 videos for %s" % (counter, i))
    try:
        vid, id = youtubeSearch(query='gamestop', key=key, start=i, end=j)
        dd = i
    except noVideos:
        print("No Videos")
        vid, id, dd = ['No videos'], ['No ID'], i
    videos += vid
    ids += id
    date.append(dd)
    if counter%50 == 0:
        sleep(5)
    counter += 1

# %% Export data
dic = {'videos': videos,
       'ids': ids,
       'dates': date
}
with open("data/gamestop_videos.json", "w") as outfile:
    json.dump(dic, outfile)

# %% Get Stats
# Import data
f = open ('data/gamestop_videos.json', "r")
data = json.loads(f.read())
ids = data['ids']

# %%
# Get stats
key = keys()
stats = []
idList = createIdStr([i for i in ids if i != 'No ID'])
for i, idStr in zip(range(0, len(idList)), idList):
    try:
        print(f"{i} - Fetching stats for {idStr}")
        stats += youtubeVideos(vidIdStr=idStr, key=key)
    except quotaLimit:
        print("Quota maxed out")

# %%
with open("data/gamestop_stats.json", "w") as outfile:
    json.dump(stats, outfile)

# %%
# Import Stats
f = open ('data/gamestop_stats.json', "r")
stats = json.loads(f.read())
idx = []
for i in stats:
    try:
        if int(i['commentCount']) > 10:
            idx.append(i['id'])
    except:
        pass

key = keys()

for i, j in zip(range(0, len(idx), 100), list(range(99, len(idx), 100))+[(len(idx))]):
    print(f"{i}:{j}")
    comments = await asyncio.gather(*[youtubeCommentThreads(i, key) for i in idx[i:i+99]])
    with open(f"data/comments/gamestop_comments_{j}.json", "w") as outfile:
        json.dump(comments, outfile)

# %%
import os
import json

counter = 1
for i in [x for x in os.listdir('data/comments') if x[:8]=='gamestop']:
    # Read file
    print(f"{counter} - {i}")
    f = open ('data/comments/'+i, "r")
    l = json.loads(f.read())

    # Clean file
    x = commentProcess(l)

    # Save
    with open(f"data/comments/processed/gamestop_comments_{counter}.json", "w") as outfile:
        json.dump(x, outfile)
    
    counter += 1

# %%
