import joblib


def classify_tweets(tweets_weighted):
    # Classifying
    clf = joblib.load('model/sentiment_classifier.pkl')
    prediction = clf.predict(tweets_weighted["Text"].values)
    tweets_weighted['Polarity'] = prediction

    return tweets_weighted

def get_polarity_average(tweets):
    # Summarize polarity
    sum = 0
    for j, tweet in tweets.iterrows():
        if tweet['Polarity'] == 'positive':
            sum = sum + tweet['Weight']
        elif tweet['Polarity'] == 'Negative':
            sum = sum - tweet['Weight']

    avg_polarity = sum / tweets.shape[0]

    return avg_polarity