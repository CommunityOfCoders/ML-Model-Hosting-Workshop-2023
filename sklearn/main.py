from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import snscrape.modules.twitter as sntwitter
import re
import contractions as cont
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
import joblib

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def remove_emoji(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)  # no emoji
    return text


def remove_repeat(text):
    newstr = ''
    for word in str(text).split():
        if len(set(word)) > 1:
            newstr += word+' '
    return newstr

def cleaner(tweets):
    cleaned_tweets = []

    for tweet in tweets:
        tweet = tweet.lower()

        tweet = re.sub('@\w*', '', tweet)
        tweet = re.sub('http\S+', '', tweet)
        tweet = re.sub('[0-9]', '', tweet)
        tweet = re.sub(r"[,!%?/;:{}()\-\*\+\[\]\.\^#]", '', tweet)
        tweet = remove_emoji(tweet)
        tweet = cont.fix(tweet)
        tweet = remove_repeat(tweet)

        tokens = word_tokenize(tweet)
        lemmatizer = WordNetLemmatizer()
        tweet = ''
        for token, tag in pos_tag(tokens):
            if tag.startswith("NN"):
                pos = 'n'
            elif tag.startswith('VB'):
                pos = 'v'
            else:
                pos = 'a'

            token = lemmatizer.lemmatize(token, pos)
            tweet += token+' '

        if tweet is not None:
            cleaned_tweets.append(tweet)
    return cleaned_tweets

@app.get('/sentiment/{hashtag}')
def get_sentiment(hashtag: str):
    maxTweets = 200
    results = {}
    nPos = 0

    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f'#{hashtag} lang:en').get_items()):
        if i > maxTweets:
            break
        tweets.append(tweet.content)
    tweets = cleaner(tweets)
    model = joblib.load('./final_classifier.pickle')
    predictions = model.predict(tweets)
    for value in predictions:
        if value == 4:
            nPos += 1

    posPer = nPos/len(tweets)
    results = {'positive': posPer}
    return results
