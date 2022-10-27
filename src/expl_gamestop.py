"""
======================
EXPLORATION - GAMESTOP
======================



"""
#%%
# Import Libraries
import asyncio
import datetime
import seaborn as sns
import json
import os
import pandas as pd
import numpy as np
import math
import spacy
from transformers import pipeline
from utils import repeated
emotion = pipeline('sentiment-analysis', model='arpanghoshal/EmoRoBERTa')

#%%
# Load Data
# Videos
f = open ('data/gamestop_videos.json', "r")
videos = json.loads(f.read())
keys = list(videos['videos'][0].keys())
df_videos = pd.DataFrame.from_dict({k:[x[k] for x in videos['videos'] if x != 'No videos'] for k in keys})
del videos

# Stats
f = open ('data/gamestop_stats.json', "r")
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
del stats

# Comments
comments = []
for i in [x for x in os.listdir('data/comments/processed') if x[:8]=='gamestop']:
    f = open ('data/comments/processed/'+i, "r")
    comments += json.loads(f.read())
keys = list(comments[0].keys())
df_comments = pd.DataFrame.from_dict({k:[x[k] for x in comments] for k in keys})
del comments
del keys

# %%
# Add dates to stats
df_vid_stats = df_videos.merge(df_stats, how='left', left_on='videoId', right_on='id')

# %%
# Convert columns
df_vid_stats['publishedAt']= pd.to_datetime(df_vid_stats['publishedAt'])
df_vid_stats['date'] = df_vid_stats['publishedAt'].dt.date

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
df_vid_stats_date_sub = df_vid_stats_date[(df_vid_stats_date['date']>=datetime.date(2020,12,1)) & (df_vid_stats_date['date']<datetime.date(2021,4,1))]
sns.lineplot(x="date", y="commentSum", data=df_vid_stats_date_sub)

# %%
# Clean data - repeated strings
df_comments['textDisplay'] = df_comments['textDisplay'].apply(lambda x: repeated(x))
# Stopwords
sp = spacy.load('en_core_web_sm')
stopwords = sp.Defaults.stop_words
df_comments['textDisplayClean'] = df_comments['textDisplay'].apply(lambda x: repeated(x))

text_tokens = 
tokens_without_sw = [w for w in word_tokenize(text) if not w in stopwords]

import spacy
nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
doc = nlp('did displaying words')
print (" ".join([token.lemma_ for token in doc]))

# %%
# Generate lists of comments
emotionInput = [x[:500] for x in df_comments['textDisplay']]

async def emotions(text: str):
    response = await emotion(text)
    return response

commentsEmotion = await asyncio.gather(*[emotions(i) for i in emotionInput])

# commentsEmotion = emotion(list(df_comments['textDisplay']))
# df_comments['emotion'] = [i['label'] for i in commentsEmotion]
# df_comments['score'] = [i['score'] for i in commentsEmotion]
# %%
