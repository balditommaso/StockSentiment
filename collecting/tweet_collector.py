# pip3 install git+https://github.com/JustAnotherArchivist/snscrape.git
from datetime import datetime

import snscrape.modules.twitter as sntwitter
import pandas as pd
from pathlib import Path
from os.path import join

from dateutil.relativedelta import relativedelta

from common.costants import target_company


def get_tweets(start_date, end_date, keyword, ticker, dir_path):
    """
    :param start_date:
    :param end_date:
    :param keyword:
    :param dir_path:
    :return:
    """
    tweets_list = []
    print("Collecting tweets")
    for i, tweet in enumerate(
            sntwitter.TwitterSearchScraper(keyword + ' since_time:' + start_date + ' until_time:' + end_date).get_items()):

        #counter
        print(i, " ", tweet.date)

        # if tweet.likeCount > tot   ### filter unpopular tweets
        tweets_list.append([tweet.user.username, tweet.user.followersCount, tweet.content, tweet.date,
                            tweet.retweetCount, tweet.likeCount, tweet.replyCount])

    # Creating a dataframe from the tweets list above
    tweets_df = pd.DataFrame(tweets_list, columns=["Account_Name", 'Number_Follower', 'Text', 'Datetime',
                                                   'Number_Retweets', 'Number_Likes', 'Number_Comments'])
    print(tweets_df)

    fname = join(dir_path, 'daily_tweets_' + ticker + '.json')


    with open(fname, 'w') as f:
        print("Saved Json: ", fname)
        tweets_df.to_json(fname, orient="records", lines=True)
    return fname

def update_tweets(arg):
    if arg == 'update':
        for company in target_company:
            fname = "data/tweets/daily_tweets_" + company['ticker'] + ".json"

            end_date = (datetime.now() + relativedelta(days=1)).strftime('%Y-%m-%d')
            start_date = (datetime.now()).strftime('%Y-%m-%d')

            fname = "../" + fname

            try:
                with open(fname, mode='r') as daily_tweets:
                    df = pd.read_json(path_or_buf=daily_tweets, orient='records', lines=True)
                    print(df.tail(1))
                    start_date = df.tail(1)['timestamp']

            except IOError:
                file = open(fname, 'w')


            get_tweets(start_date, end_date, company['name'], company['ticker'], "../data/tweets/")

    return 0

if __name__ == "__main__":
    update_tweets('update')