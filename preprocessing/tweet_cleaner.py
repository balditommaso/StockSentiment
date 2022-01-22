import pandas as pd
from langdetect import detect
import re

from common.costants import target_company


def tweet_pruning(df, keyword, ticker):
    """
    to remove tweets where the keyword is in the username only
    Remove rows where the text do not contain the keyword
    :param df:
    :param keyword:
    :param ticker:
    :return:
    """
    for index, row in df.iterrows():
        find_keyword = row['Text'].find(keyword)
        find_ticker = row['Text'].find(ticker)
        # search keyword
        if find_keyword == -1 and find_ticker == -1:
            df.drop(index, inplace=True)
            continue
        # select only english tweet
        try:
            if detect(row['Text']) != 'en':
                df.drop(index, inplace=True)
        except:
            df.drop(index, inplace=True)
    return df


def remove_special_char(text):
    """
    Apply to the text all the RegEx to clean the tweet text
    :param text:
    :return:
    """
    # remove digits
    text = ''.join(i for i in text if not i.isdigit())
    # remove emoji
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               "]+", flags=re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    # remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    # remove \n
    text = text.replace('\n', ' ')
    # remove non-ASCII character
    text = re.sub('([^\x00-\x7F])+', '', text)
    # Convert www.* or https?://* to empty strings
    text = re.sub('(http[A-Za-z]*)', '', text)
    # Convert @username to empty strings
    text = re.sub(r'@[^\s]+', '', text)
    # remove multiple spaces
    text = " ".join(text.split())

    return text


def filter_tweets(tweets, ticker):
    """
    filter all the JSON files given by path and save a new files with the
    results
    :param path:
    :return:
    """
    for company in target_company:
        if company['ticker'] == ticker:
            company_name = company['name']

    tweets['Real_Text'] = tweets['Text']
    # keep lowercase
    tweets['Text'] = tweets['Text'].str.lower()
    # remove noisy tweets
    tweets = tweet_pruning(tweets, company_name, ticker)
    # remove special char
    tweets['Text'] = tweets['Text'].apply(remove_special_char)
    return tweets


# TEST
if __name__ == "__main__":
    fname = '../data/TEST_FILTER.json'
    with open(fname, mode='r') as file:
        df = pd.read_json(path_or_buf=file, orient='records', lines=True)
    print(df['Text'])
    clean_df = filter_tweets(df, 'AMZN')
    print(clean_df['Text'])


