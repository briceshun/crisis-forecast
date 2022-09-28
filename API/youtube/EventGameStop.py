# %% Import Modules
# Base
from datetime import datetime, timedelta
from time import sleep
import pandas as pd
#import seaborn as sns

# Custom YouTube Functions
from functions.search import *
from functions.videos import *
from functions.commentThreads import *

# %% Date Range
startdate = datetime.strptime('2020-12-01', '%Y-%m-%d')
enddate = datetime.strptime('2021-07-31', '%Y-%m-%d')

dates = []
dates1 = []

while startdate <= enddate:
    dates.append(startdate.strftime('%Y-%m-%d'))
    dates1.append((startdate + timedelta(days=1)).strftime('%Y-%m-%d'))
    startdate += timedelta(days=1)

# %% Get Videos
videos, ids = [], []
counter = 1
for i, j in zip (dates, dates1):
    print(f"%s - Fetching top 50 videos for %s" % (counter, i))
    try:
        vid, id = youtubeSearch(query = 'gamestop', start=i, end=j)
        videos += vid
        ids += id
    except:
        print('skip')
        pass
    if counter%50 == 0:
        sleep(5)
    counter += 1
# %%
