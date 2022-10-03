# %% Import Modules
# Base
from datetime import datetime, timedelta
from time import sleep
import pandas as pd
#import seaborn as sns

# Custom YouTube Classes and Functions
from classes.api_key import *
from functions.search import *
from functions.videos import *
from functions.commentThreads import *

# %% Date Range
startdate = datetime.strptime('2020-01-04', '%Y-%m-%d')
enddate = datetime.strptime('2021-01-06', '%Y-%m-%d')

dates = []
dates1 = []

while startdate <= enddate:
    dates.append(startdate.strftime('%Y-%m-%d'))
    dates1.append((startdate + timedelta(days=1)).strftime('%Y-%m-%d'))
    startdate += timedelta(days=1)

# %% Get Videos
key = yt_api_key()
videos, ids, date = [], [], []
counter = 1
for i, j in zip (dates, dates1):
    print(f"%s - Fetching top 50 videos for %s" % (counter, i))
    try:
        vid, id, dd = youtubeSearch(query='gamestop', key=key, start=i, end=j), i
    except NoVideosError:
        vid, id, dd = ['No videos'], ['No ID'], i
    videos += vid
    ids += id
    date += dd
    if counter%50 == 0:
        sleep(5)
    counter += 1
# %%
