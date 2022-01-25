# pip3 install git+https://github.com/JustAnotherArchivist/snscrape.git
from datetime import datetime

import pytz
import snscrape.modules.twitter as sntwitter
import pandas as pd
from dateutil.relativedelta import relativedelta
from common.costants import target_company


def update_tweets(ticker):
    """
    :param start_date:
    :param end_date:
    :param keyword:
    :param dir_path:
    :return:
    """
    if ticker == 'init':
        for company in target_company:
            fname = "data/tweets/tweets_" + company['ticker'] + ".json"
            with open(fname, mode='r') as saved_tweets:
                df = pd.read_json(path_or_buf=saved_tweets, orient='records', lines=True)
            if df.size > 0:
                df['Datetime'] = pd.to_datetime(df['Datetime'])
                last_insert = df['Datetime'].max()
                today = datetime.utcnow()
                # check if need to update
                if today.year == last_insert.year and today.month == last_insert.month and today.day == last_insert.day:
                    print(company['ticker'] + ' already updated')
                    continue

            start_date = str(int(datetime(today.year, today.month, today.day-1, 16, 0, 0, tzinfo=pytz.utc).timestamp()))
            end_date = str(int(datetime(today.year, today.month, today.day, 15, 59, 0, tzinfo=pytz.utc).timestamp()))
            tweets = download_tweet(company['ticker'], company['name'], start_date, end_date)
            with open(fname, mode='w') as f:
                tweets.to_json(fname, orient="records", lines=True, date_format='iso')
    else:
        for company in target_company:
            if ticker == company['ticker']:
                name = company['name']
        fname = "data/tweets/tweets_" + ticker + ".json"
        with open(fname, mode='r') as saved_tweets:
            df = pd.read_json(path_or_buf=saved_tweets, orient='records', lines=True)
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        last_insert = df['Datetime'].max()

        start_date = str(int((last_insert + relativedelta(seconds=1)).timestamp()))
        end_date = str(int(datetime.utcnow().timestamp()))
        tweets = download_tweet(ticker, name, start_date, end_date)
        if tweets.size > 0:
            df.append(tweets)
        with open(fname, mode='w') as f:
            df.to_json(fname, orient="records", lines=True, date_format='iso')


def download_tweet(ticker, name, start_date, end_date):
    tweets_list = []
    print("Collecting tweets: " + ticker + "\n")
    keyword = name + " " + ticker
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(keyword + ' since_time:' + start_date +
                                                             ' until_time:' + end_date).get_items()):
        print("\t" + str(i), " ", tweet.date)
        tweets_list.append([tweet.user.username, tweet.user.followersCount, tweet.content, tweet.date, ticker])

    # Creating a dataframe from the tweets list above
    tweets_df = pd.DataFrame(tweets_list, columns=["Account_Name", 'Number_Follower', 'Text', 'Datetime', 'Ticker'])
    print("Finish. \n")
    return tweets_df


# TEST
if __name__ == "__main__":
    rs = download_tweet('TSLA', 'tesla', str(int((datetime.utcnow() - relativedelta(hours=1)).timestamp())), str(int(datetime.utcnow().timestamp())))
    print(rs)