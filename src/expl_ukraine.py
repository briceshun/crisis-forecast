"""
======================
EXPLORATION - ukraine
======================



"""
#%%
# Import Libraries
import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from utils import noOutlier, emotionGroup, describeEvent, plotLine, plotStack, clusterKMeans

#%%
# Load Data
# Videos
f = open ('data/ukraine_videos.json', "r")
videos = json.loads(f.read())
keys = list(videos['videos'][0].keys())
df_videos = pd.DataFrame.from_dict({k:[x[k] for x in videos['videos'] if x != 'No videos'] for k in keys})
del videos

#%%
# Stats
f = open ('data/ukraine_stats.json', "r")
stats = json.loads(f.read())
keys = list(stats[0].keys())
dict = {k:[] for k in keys}
for k in keys:
    x = []
    for i in stats:
        try:
            dict[k].append(i[k])
        except:
            dict[k].append(np.nan)
df_stats = pd.DataFrame.from_dict(dict)
df_stats.fillna(0, inplace=True)
for col in ['viewCount', 'likeCount', 'favoriteCount', 'commentCount']:
    df_stats[col] = df_stats[col].astype(int)
del stats

#%%
# Comments
comments = []
for i in [x for x in os.listdir('data/comments/processed') if x[:7]=='ukraine']:
    f = open ('data/comments/processed/'+i, "r")
    comments += json.loads(f.read())
keys = list(comments[0].keys())
df_comments = pd.DataFrame.from_dict({k:[x[k] for x in comments] for k in keys})
del comments
del keys

#%%
# Group emotions
df_comments['emotionraw'] = df_comments['emotion']
df_comments['emotion'] = df_comments['emotionraw'].apply(lambda x: emotionGroup(x))
df_comments['valence'] = df_comments['emotionraw'].apply(lambda x: emotionGroup(x, valence=True))

# %%
# Add dates to stats
df_vid_stats = df_videos.merge(df_stats, how='left', left_on='videoId', right_on='id')
df_vid_stats = noOutlier(df_vid_stats, ['viewCount', 'likeCount', 'commentCount'])

# Describe
desc_vid_stats = describeEvent(df_vid_stats, ['viewCount', 'likeCount', 'commentCount'])
desc_vid_stats

# %%
# Convert columns
df_vid_stats['publishedAt']= pd.to_datetime(df_vid_stats['publishedAt'])
df_vid_stats['date'] = df_vid_stats['publishedAt'].dt.date
#df_vid_stats['week'] = df_vid_stats['publishedAt'].apply(lambda x: x - datetime.timedelta(days=x.weekday()))

for col in ['viewCount', 'likeCount', 'favoriteCount', 'commentCount']:
    df_vid_stats[col] = pd.to_numeric(df_vid_stats[col])

# Group and summarise
df_vid_stats_date = df_vid_stats.groupby('date')\
                                .agg(   viewSum=('viewCount', 'sum'),
                                        likeSum=('likeCount', 'sum'),
                                        favoriteSum=('favoriteCount', 'sum'),
                                        commentSum=('commentCount', 'sum'),
                                        viewAvg=('viewCount', 'mean'),
                                        likeAvg=('likeCount', 'mean'),
                                        favoriteAvg=('favoriteCount', 'mean'),
                                        commentAvg=('commentCount', 'mean'),
                                )\
                                .reset_index()

# Plot total views each day
plotLine(df_vid_stats_date, 'commentSum', ['2021-12-01', '2022-04-01'])

# %%
# Convert columns
df_comments['publishedAt']= pd.to_datetime(df_comments['publishedAt'])
df_comments['date'] = df_comments['publishedAt'].dt.date

# Summarise comment emotions
df_comments_emotion, df_comments_emotion100 = plotStack(df_comments, ['2021-01-01', '2022-04-01'])

# %%
# Summarise comment valence
df_comments_valence, df_comments_valence100 = plotStack(df_comments, ['2021-01-01', '2022-04-01'], valence=True)

# %%
# Clustering
phases = clusterKMeans(df_comments_emotion, df_comments_emotion100, 3)
df_comments_emotion100['phase'] = phases
describeEvent(df_comments_emotion100, df_comments_emotion100.columns.drop(['phase', 'date']), clustered = True)

# %%
