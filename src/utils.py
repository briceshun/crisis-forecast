"""
===================
UTILITIES
===================
User defined functions

- checkAPI      : Try API call and rotate keys if quota limit HTTP error raised
- cleanUp       : Extract data from response and reshape
- createIdStr   : Create list of concatenated ids (max 600 characters) for multiple api queries
- commentProcess: Extract comments from API response
- repeated      : Find repeated strings and get unique values
- textClean     : Clean text string - remove stopwords and lemmatise
- emotionModel  : Apply emotion model on text 
- emotionGroup  : DataFrame containing emotion groupings
- plotLine      : Create subsetted line chart
- plotStack     : Create subsetted stacked bar chart
- noOutlier     : Clean dataframe by removing outliers
- describeEvent : Create summary statistics
- clusterKmeans : Apply KMeans clustering algorithm
- normalityTest : Check if variables are normally distributed
- diffTest      : Check if differences are significant

"""

# %%
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from  matplotlib.ticker import PercentFormatter
import json
import pandas as pd
import numpy as np
import re
import seaborn as sns
import spacy
from googleapiclient.errors import HttpError
from time import sleep
from transformers import pipeline
from sklearn.cluster import KMeans
from scipy.stats import shapiro, levene, ttest_ind, mannwhitneyu

from models import noVideos, characterLimit, commentsDisabled

pd.set_option('display.max_columns', None)

# %%
def checkAPI(key):
    def decorator(function):
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except HttpError as err:
                # Quota exceeded
                if 'disabled comments' in json.loads(err.content)['error']['errors'][0]['message']:
                    raise commentsDisabled
                elif err.resp.status == 403:
                    key.next_key()
                    return function(*args, **kwargs)
                # Server error - retry 2 more times
                elif err.resp.status in [500, 503]:
                    for i in range(0, 2):
                        print(f"Retry: {i}")
                        sleep(5)
                        return wrapper(function(*args, **kwargs))
                # API length exceeds character limit
                elif err.resp.status == 400:
                    raise characterLimit
                # Others
                else:
                    raise Exception('Unknown Error')
        return wrapper
    return decorator

# %%
def cleanUp(data):
    output = []

    # Check if response is not null
    if len(data['items']) == 0:
        raise noVideos
    else:
        keys = list(data['items'][0].keys())
        keys2 = list(data['items'][0][keys[1]].keys())

        # Check if CommentThreads API
        if len(keys2) == 1:
            # CommentThreads API
            keys3 = list(data['items'][0]['snippet']['topLevelComment'].keys())
            # Loop over all items in response
            for item in data['items']:
                # Create variables to store data
                dict = item['snippet']['topLevelComment']
                # Extract snippet dict to combine
                snippet = dict['snippet']
                # Loop over all keys other than Snippet
                for i in keys3[1:]:
                    snippet |= {i: dict[i]}
                # Add replies
                try:
                    snippet |= dict['replies']
                except:
                    pass
                output.append(snippet)

        # Search and Videos API
        else:
            try:
                # Loop over all items in response of Search API
                for item in data['items']:
                    output.append(item[keys[0]] | item[keys[1]])
            except TypeError:
                # Create dict for each item and append other dict for Videos API
                for item in data['items']:
                    output.append({keys[0]: item[keys[0]]} | item[keys[1]])
        return output

# %%
def createIdStr(
    vidId: list,
    maxLen: int = 600
):
    output = []
    # Iterate over ids step by maxLen/concatLen + 1
    # where concatLen = 11 + 1 (id length + comma)
    n = round(maxLen/12)
    for i in range(0, len(vidId), n):
        # If last id
        if i == len(vidId):
            output.append(vidId[i])
        # Last batch of ids
        elif i + n > len(vidId):
            output.append(','.join(vidId[i:]))
        # Concat normally for others
        else:
            output.append(','.join(vidId[i:i+n]))
    return output
# %%
def commentProcess(data):
    output = []
    # Loop over asyncs
    for f in data:
        # Loop over items
        for item in f:
            x = item['snippet']['topLevelComment']['snippet']
            output += [{
                'commentid': item['id'], 'videoId': x['videoId'], 'textDisplay': x['textDisplay'], 'textOriginal': x['textOriginal'], 'authorDisplayName': x['authorDisplayName'], 'publishedAt': x['publishedAt'], 'updatedAt': x['updatedAt']
            }]
    return output

# %%
def repeated(s):
    match = re.compile(r"(.+?)\1+$").match(s)
    return match.group(1) if match else s


# %%
# Load model
sp = spacy.load('en_core_web_sm')
stopwords = sp.Defaults.stop_words

def textClean(
    text: str,
    length: int = 500
) -> str:
    # Tokenise, remove stopwords text, and lemmatise
    output = ' '.join([token.lemma_ for token in sp(text)
                      if not token.text in stopwords])
    # Shorten
    output = output[:length]
    return output


# %%
emotion = pipeline('sentiment-analysis', model='arpanghoshal/EmoRoBERTa')
def emotionModel(
    text: str
) -> list:
    return emotion(text)

# %%
def emotionGroup(
    emotion: str,
    valence: bool = False
) -> str:

    data = {
        'admiration': ['Affection', 'Positive'],
        'amusement': ['Happiness', 'Positive'],
        'anger': ['Anger', 'Negative'],
        'annoyance': ['Anger', 'Negative'],
        'approval': ['Satisfaction', 'Positive'],
        'caring': ['Affection', 'Positive'],
        'confusion': ['Fear', 'Negative'],
        'curiosity': ['Fear', 'Negative'],
        'desire': ['Fear', 'Negative'],
        'disappointment': ['Depression', 'Negative'],
        'disapproval': ['Anger', 'Negative'],
        'disgust': ['Contempt', 'Negative'],
        'embarrassment': ['Depression', 'Negative'],
        'excitement': ['Happiness', 'Positive'],
        'fear': ['Fear', 'Negative'],
        'gratitude': ['Satisfaction', 'Positive'],
        'grief': ['Depression', 'Negative'],
        'joy': ['Happiness', 'Positive'],
        'love': ['Affection', 'Positive'],
        'nervousness': ['Fear', 'Negative'],
        'optimism': ['Happiness', 'Positive'],
        'pride': ['Affection', 'Positive'],
        'realization': ['Satisfaction', 'Positive'],
        'relief': ['Happiness', 'Positive'],
        'remorse': ['Contempt', 'Negative'],
        'sadness': ['Depression', 'Negative'],
        'surprise': ['Happiness', 'Positive'],
        'neutral': ['Neutral', 'Neutral'],
        'error': ['Neutral', 'Neutral']
    }

    if emotion.lower() == 'error':
        return 'error'
    else:
        if valence:
            return data[emotion.lower()][1]
        else:
            return data[emotion.lower()][0]

# %%
def plotLine(
    df,
    variable: str,
    period: list = []
):

    # Subset data
    if len(period) != 0:
        df_subset = df[(df['date'] >= datetime.strptime(period[0], '%Y-%m-%d').date())
                       & (df['date'] <= datetime.strptime(period[1], '%Y-%m-%d').date())]
    else:
        df_subset = df

    # Create plot
    #sns.set(rc={'figure.figsize':(11.7,3.27)})
    sns.set_style(style='white') 
    plot = sns.lineplot(x='date', y=variable, data=df_subset)
    # Formatting
    # x-axis
    plot.set(xlabel=None)
    plt.xticks(rotation=45)
    # y-axis
    plot.set(ylabel='Total # of Comments')
    plot.yaxis.set_major_formatter(lambda y, p: f'{y/1000:.0f}k')

    return plot

# %%
def plotStack(
    df,
    period: list = [],
    emotions: list = [],
    valence: bool = False,
    width: float = 1.0
    ):

    # Assign colours to emotions and valence
    mapEmotion = {
        'Affection': 'deepskyblue',
        'Happiness': 'green',
        'Satisfaction': 'turquoise',
        'Anger': 'firebrick',
        'Contempt': 'darkorange',
        'Depression': 'maroon',
        'Fear': 'gold',
        'Neutral': 'yellow'
    }
    mapValence = {
        'Positive': 'green',
        'Negative': 'firebrick'
    }
    if valence:
        mapper = mapValence
        sentiment = 'valence'
    else:
        mapper = mapEmotion
        sentiment = 'emotion'

    # Subset period
    if len(period) > 0:
        df_subset = df[(df['date'] >= datetime.strptime(period[0], '%Y-%m-%d').date()) & (df['date'] <= datetime.strptime(period[1], '%Y-%m-%d').date())]
    else:
        df_subset = df.copy(deep=True)

    # Unstack
    df_stack = df_subset[~df_subset.emotion.isin(['Neutral', 'error'])][['date', sentiment]]\
        .groupby('date')[sentiment]\
        .value_counts(normalize=False)\
        .unstack(sentiment)\
        .reset_index()
    
    df_stack100 = df_subset[~df_subset.emotion.isin(['Neutral', 'error'])][['date', sentiment]]\
        .groupby('date')[sentiment]\
        .value_counts(normalize=True)\
        .unstack(sentiment)\
        .reset_index()

    # Subset emotions
    if len(emotions) > 0:
        orderMap = [e for e in mapper if e != 'Neutral' and e in emotions]
        orderCol = ['date']+orderMap
        colourMap = [mapper[e] for e in mapper if e != 'Neutral' and e in emotions]
        df_stack = df_stack[orderCol]
    else:
        orderMap = [e for e in mapper if e != 'Neutral']
        orderCol = ['date']+orderMap
        colourMap = [mapper[e] for e in mapper if e != 'Neutral']

    # Create plot
    plot_stack = df_stack[orderCol].plot(x='date', kind='bar', stacked=True, color=colourMap, width=width)
    plot_stack.set(xlabel=None)
    plot_stack.legend_.set_title(None)
    plot_stack.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plot_stack.yaxis.set_major_formatter(lambda y, p: f'{y/1000:.0f}k')
    plt.xticks(rotation=45)

    plot_stack100 = df_stack100[orderCol].plot(x='date', kind='bar', stacked=True, color=colourMap, legend=None, width=width)
    plot_stack100.set(xlabel=None)
    plot_stack100.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plot_stack100.yaxis.set_major_formatter(lambda y, p: f'{y*100:.0f}'+'%')
    plt.xticks(rotation=45)

    return df_stack, df_stack100

# %%
def noOutlier(
    df,
    cols: list,
    sd: float = 3
    ):
    
    # Create copy
    output = df.copy(deep=True)

    # Drop rows with outliers
    for c in cols:
        UB = np.mean(output[c]) + (sd * np.std(output[c]))
        output = output[output[c] <= UB]
    
    return output

# %%
def describeEvent(
    df,
    cols: list,
    periods: list = None,
    clustered: bool = False,
    func: list = ['count', 'mean', 'std', 'var', 'min', 'max']
    ):
    # Overall
    overall = df[cols].agg(func).reset_index()

    # Periods
    if periods:
        end = max(df['date'])
        # Create phase lists
        phases = [datetime.strptime(p, '%Y-%m-%d').date() for p in phases]
        phase_list = [[phases[0], phases[1]-timedelta(days=1)]]
        for i in range(1, len(phases)):
            if i < len(phases)-1:
                phase_list.append([phases[i], phases[i+1]-timedelta(days=1)])
            else:
                phase_list.append([phases[i], end])
        # Create labels
        def labeller(x):
            for p in phase_list:
                if x >= p[0] and x <= p[1]:
                    return p[0]
        # Label data
        df_labelled = df.copy(deep=True)
        df_labelled['phase'] = df_labelled['date'].apply(lambda x: labeller(x))
        # Aggregate
        phased = df[['phase']+cols].groupby('phase').agg(func).reset_index()
        
        return overall, phased

    # Clusters
    if clustered:
        agg_func = {c: ['mean', 'std', 'var', 'min', 'max'] for c in cols}
        agg_func['date'] = ['min', 'max']
        return df.groupby('phase').agg(agg_func).reset_index()

    return overall

# %%
def clusterKMeans(
    df,
    df100,
    k: int = 3,
    interval: int = 2
    ):
    # Clean input data
    x = df100[df100.columns.drop('date')]
    df_input = df[df.columns.drop('date')].reset_index()

    # Cluster
    kmeans = KMeans(n_clusters=k).fit(x)
    clusters = kmeans.predict(x)

    # Create df for graph
    df_input['total'] = df_input[df_input.columns.drop('index')].sum(axis=1)
    df_input['clusters'] = clusters
    df_select = df_input[['total', 'clusters']]
    df_select['date'] = df['date']
    # Reorder Clusters
    phase_list = []
    for c in clusters:
        if len(phase_list) == k:
            break
        else:
            if c not in phase_list:
                phase_list.append(c)
    df_select['phase'] = ['Phase ' + str(p) for p in [phase_list.index(c)+1 for c in clusters]]
    # Pivot
    df_graph = df_select.pivot(index='date', columns='phase', values='total').reset_index()
    
    # Plot
    plot = df_graph.plot(x = 'date', kind='bar', stacked=True, width=1.0)
    plot.set(xlabel=None)
    plot.legend_.set_title(None)
    plot.xaxis.set_major_locator(mdates.WeekdayLocator(interval=interval))
    plot.set(ylabel='Total # of Comments')
    plot.yaxis.set_major_formatter(lambda y, p: f'{y/1000:.0f}k')
    plt.xticks(rotation=45)

    return ['Phase ' + str(p) for p in [phase_list.index(c)+1 for c in clusters]]

# %%
def normalityTest(
    df,
    cols: list
    ):
    return pd.DataFrame({
        'variable': cols,
        'pvalue': [shapiro(df[c]).pvalue for c in cols]
        })

# %%
def diffTest(
    df,
    df_norm,
    n: int = 2
    ):
    # Create test pairs
    cols = list(df_norm['variable'])
    normal = list(df_norm['normal'])
    pairs = []
    for i in range(1, n+1):
        for j in range(1, n+1):
            if i < j:
                phase_label = ['Phase ' + str(i), 'Phase ' + str(j)]
                if phase_label not in pairs:
                    pairs.append(phase_label)

    # Loop over pairs to test
    output = {'pair': [p[0] + '-' + p[1] for p in pairs]}
    output |= {c: [] for c in cols}

    for p in pairs:
        for c, n in zip(cols, normal):
            x = df[c][df['phase'] == p[0]]
            y = df[c][df['phase'] == p[1]]
            # Normal
            if n == 1:
                # Check equal variance
                if levene(x, y, center='mean').pvalue < 0.05:
                    output[c].append(ttest_ind(a=x, b=y, equal_var=True).pvalue)
                else:
                    output[c].append(ttest_ind(a=x, b=y, equal_var=False).pvalue)
            # Non parametric
            else:
                stat, pval = mannwhitneyu(x, y)
                output[c].append(pval)

    return pd.DataFrame(output)

# %%
def plotBox(
    df,
    wrap: int = 2
    ):
    sns.set(font_scale=1.25)
    sns.set_style(style='white') 
    g = sns.catplot(
        data=df, x='phase', y='value',
        col='emotion', kind='box', col_wrap = wrap
        )
    for ax in g.axes.flat:
        ax.yaxis.set_major_formatter(PercentFormatter(1))
    g.set(xlabel=None)
    g.set(ylabel="Overall Proportion")
    plt.show()