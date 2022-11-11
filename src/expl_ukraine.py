"""
======================
EXPLORATION - ukraine
======================



"""
#%%
# Import Libraries
import datetime
import seaborn as sns
import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#from utils import emotionGroup

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
for col in ['viewCount', 'likeCount', 'commentCount']:
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
def emotionGroup(
    emotion: str,
    valence: bool = False
    ) -> str:
    
    data = {'admiration': ['Affection', 'Positive'],
            'amusement' : ['Happiness', 'Positive'],
            'anger' : ['Anger', 'Negative'],
            'annoyance' : ['Anger', 'Negative'],
            'approval' : ['Satisfaction', 'Positive'],
            'caring' : ['Affection', 'Positive'],
            'confusion' : ['Fear', 'Negative'],
            'curiosity' : ['Fear', 'Negative'],
            'desire' : ['Fear', 'Negative'],
            'disappointment' : ['Depression', 'Negative'],
            'disapproval' : ['Anger', 'Negative'],
            'disgust' : ['Contempt', 'Negative'],
            'embarrassment' : ['Depression', 'Negative'],
            'excitement' : ['Happiness', 'Positive'],
            'fear' : ['Fear', 'Negative'],
            'gratitude' : ['Satisfaction', 'Positive'],
            'grief' : ['Depression', 'Negative'],
            'joy' : ['Happiness', 'Positive'],
            'love' : ['Affection', 'Positive'],
            'nervousness' : ['Fear', 'Negative'],
            'optimism' : ['Happiness', 'Positive'],
            'pride' : ['Affection', 'Positive'],
            'realization' : ['Satisfaction', 'Positive'],
            'relief' : ['Happiness', 'Positive'],
            'remorse' : ['Contempt', 'Negative'],
            'sadness' : ['Depression', 'Negative'],
            'surprise' : ['Happiness', 'Positive'],
            'neutral' : ['Neutral', 'Neutral'],
            'error' : ['Neutral', 'Neutral']
            }
    if valence:
        return data[emotion.lower()][1]
    else:
        return data[emotion.lower()][0]

# Group emotions
df_comments['emotionraw'] = df_comments['emotion']
df_comments['emotion'] = df_comments['emotionraw'].apply(lambda x: emotionGroup(x))
df_comments['valence'] = df_comments['emotionraw'].apply(lambda x: emotionGroup(x, valence=True))

# %%
# Add dates to stats
df_vid_stats = df_videos.merge(df_stats, how='left', left_on='videoId', right_on='id')

# %%
# Convert columns
df_vid_stats['publishedAt']= pd.to_datetime(df_vid_stats['publishedAt'])
df_vid_stats['date'] = df_vid_stats['publishedAt'].dt.date
df_vid_stats['week'] = df_vid_stats['publishedAt'].apply(lambda x: x - datetime.timedelta(days=x.weekday()))

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
df_vid_stats_date_sub = df_vid_stats_date[(df_vid_stats_date['date']>=datetime.date(2021,12,1)) & (df_vid_stats_date['date']<datetime.date(2022,4,1))]
sns.lineplot(x="date", y="commentSum", data=df_vid_stats_date_sub)

# %%
# Convert columns
df_comments['publishedAt']= pd.to_datetime(df_comments['publishedAt'])
df_comments['date'] = df_comments['publishedAt'].dt.date

# Summarise comment emotions
df_comments_date = df_comments[df_comments['emotion'] != 'Neutral'][['date', 'emotion']]\
                    .groupby('date')['emotion']\
                    .value_counts(normalize=False)\
                    .unstack('emotion')\
                    .reset_index()
df_comments_date1 = df_comments[df_comments['emotion'] != 'Neutral'][['date', 'emotion']]\
                    .groupby('date')['emotion']\
                    .value_counts(normalize=True)\
                    .unstack('emotion')\
                    .reset_index()

# # Create stacked bar chart
df_comments_date_sub = df_comments_date[(df_comments_date['date']>=datetime.date(2022,1,1)) & (df_comments_date['date']<datetime.date(2022,4,1))]
df_comments_date_sub.plot(x='date', kind='bar', stacked=True)
plt.show()
df_comments_date_sub1 = df_comments_date1[(df_comments_date1['date']>=datetime.date(2022,1,1)) & (df_comments_date1['date']<datetime.date(2022,4,1))]
df_comments_date_sub1.plot(x='date', kind='bar', stacked=True, legend=None)
plt.show()

# %%
# Summarise comment valence
df_comments_date = df_comments[df_comments['valence'] != 'Neutral'][['date', 'valence']]\
                    .groupby('date')['valence']\
                    .value_counts(normalize=False)\
                    .unstack('valence')\
                    .reset_index()
df_comments_date1 = df_comments[df_comments['valence'] != 'Neutral'][['date', 'valence']]\
                    .groupby('date')['valence']\
                    .value_counts(normalize=True)\
                    .unstack('valence')\
                    .reset_index()

# # Create stacked bar chart
df_comments_date_sub = df_comments_date[(df_comments_date['date']>=datetime.date(2022,1,1)) & (df_comments_date['date']<datetime.date(2022,4,1))]
df_comments_date_sub.plot(x='date', kind='bar', stacked=True)
plt.show()
df_comments_date_sub1 = df_comments_date1[(df_comments_date1['date']>=datetime.date(2022,1,1)) & (df_comments_date1['date']<datetime.date(2022,4,1))]
df_comments_date_sub1.plot(x='date', kind='bar', stacked=True, legend=None)
plt.show()

# %%
