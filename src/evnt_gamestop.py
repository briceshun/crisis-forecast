"""
================
EVENT - GAMESTOP
================



"""

# %%
import json
from datetime import datetime, timedelta
from time import sleep
from func_search import youtubeSearch
from models import keys, noVideos

# %% Date Range
startdate = datetime.strptime('202-12-01', '%Y-%m-%d')
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
    date += dd
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

# %%
