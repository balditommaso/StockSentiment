from textblob import TextBlob
import pandas as pd

def get_subjectivity(text):
    return TextBlob(text).sentiment.subjectivity


def get_polarity(text):
    return TextBlob(text).sentiment.polarity


def save_file(df):
    """
    Save a DataFrame inside a JSON file call with ticker
    :param ticker:
    :param df:
    :return:
    """
    fname = '../data/sentimentTweets_test.json'
    with open(fname, 'w') as f:
        print("Saved JSON: ", fname)
        df.to_json(fname, orient="records", lines=True)


def add_score(df):
    df['Subjectivity'] = df['Text'].apply(get_subjectivity)
    df['Polarity'] = df['Text'].apply(get_polarity)
    return df

def add_sentiment(path):
    df = pd.read_json(path, lines=True)
    df_score = add_score(df)
    for index, row in df_score.iterrows():
        # FILTER BY OBJECTIVITY
        if row['Polarity'] > 0.3:
            row['Sentiment'] = 'positive'
        elif row['Polarity'] < -0.3:
            row['Sentiment'] = 'negative'
        else:
            row['Sentiment'] = 'neutral'
    save_file(df_score)
if __name__ == '__main__':
    path = '../data/filteredTweets_AMZN_test.json'
    add_sentiment(path)