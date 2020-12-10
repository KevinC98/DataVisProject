from flask import Flask, render_template, request
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import os
import pandas as pd
import json

from twitter_auth_mock import API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET

import tweepy as tp

auth = tp.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

api = tp.API(auth)

app = Flask(__name__)

app.config['CSV_FOLDER'] = 'static/CSV'

analyser = SentimentIntensityAnalyzer()

def sentiment_analyser_score(data):
    score = analyser.polarity_scores(data)
    print(score)


@app.route('/chart')
def chart():
    df = pd.read_csv('static/CSV/Book1.csv', header=None)
    series = {}

    series['name'] = 'Tweets'
    series['colorByPoint'] = 'true'

    current_value = None
    data = []
    series_data = []
    value = 0

    for row in df.iterrows():

        ent = row[1]

        id = ent[0]
        cat = ent[1]
        val = ent[2]

        if current_value == None:
            current_value = id

        if id != current_value:
            list_item = {}
            series_list_item = {}

            list_item['name'] = current_value
            list_item['id'] = current_value
            list_item['data'] = data

            series_list_item['name'] = current_value
            series_list_item['y'] = value
            series_data.append(series_list_item)

            data = []
            value = 0
            current_value = id

        data.append([cat, val])
        value += val

    list_item = {}
    series_list_item = {}

    list_item['name'] = current_value
    list_item['id'] = current_value
    list_item['data'] = data

    series_list_item["name"] = current_value
    series_list_item["y"] = value

    series_data.append(series_list_item)

    data = []
    value = 0

    series['data'] = series_data

    series = json.dumps(series)


    print(series)
    return render_template('chart.html', series=series)



@app.route('/', methods=['GET', 'POST'])
def process_query():
    if request.method == 'POST':
        query = request.form['query']
        tweets = api.search(q=query)
        for tweet in tweets:
            print(tweet.text)
            analysis = TextBlob(tweet.text)
            print(analysis.sentiment)
            sentiment_analyser_score(tweet.text)
        return render_template('results.html', tweets=tweets)
    else:
        return render_template('index.html')




if __name__ == '__main__':
    app.run()