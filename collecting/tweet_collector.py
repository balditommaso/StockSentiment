# pip3 install git+https://github.com/JustAnotherArchivist/snscrape.git
from datetime import datetime
import snscrape.modules.twitter as sntwitter
import pandas as pd
from dateutil.relativedelta import relativedelta
from common.costants import target_company


def get_tweets(arg):
    """
    :param start_date:
    :param end_date:
    :param keyword:
    :param dir_path:
    :return:
    """
    for company in target_company:
        fname = "data/tweets/tweets_" + company['ticker'] + ".json"
        # adapt the research
        if arg == 'init':
            fname = "../" + fname
            start_date = str(int(datetime(2021, 1, 18).timestamp()))  # 2021-01-18
            end_date = str(int(datetime(2022, 1, 18).timestamp()))    # 2022-01-18
            mode = 'w'
        elif arg == 'update':
            end_date = str(int(datetime.now().timestamp()))
            with open(fname, mode='r') as saved_tweets:
                df = pd.read_json(path_or_buf=saved_tweets, orient='records', lines=True)
            last_insert = df.head(1)['Datetime'].values[0]
            start_date = pd.to_datetime(str(last_insert))
            start_date = str(int((start_date + relativedelta(seconds=1)).timestamp()))
            mode = 'a'

        tweets_list = []
        print("Collecting tweets: " + company['ticker'] + "\n")
        keyword = company['name'] + " " + company['ticker']
        for i, tweet in enumerate(sntwitter.TwitterSearchScraper(keyword + ' since_time:' + start_date +
                                                                 ' until_time:' + end_date).get_items()):
            print("\t" + str(i), " ", tweet.date)
            tweets_list.append([tweet.user.username, tweet.user.followersCount, tweet.content, tweet.date,
                                tweet.retweetCount, tweet.likeCount, tweet.replyCount])

        # Creating a dataframe from the tweets list above
        tweets_df = pd.DataFrame(tweets_list, columns=["Account_Name", 'Number_Follower', 'Text', 'Datetime',
                                                       'Number_Retweets', 'Number_Likes', 'Number_Comments'])
        print("Finish. \n")
        print(tweets_df)

        with open(fname, mode) as f:
            tweets_df.to_json(fname, orient="records", lines=True)


#def update_tweets(arg):
#    if arg == 'update':
#        for company in target_company:
#            fname = "data/tweets/daily_tweets_" + company['ticker'] + ".json"
#
#            end_date = (datetime.now() + relativedelta(days=1)).strftime('%Y-%m-%d')
#            start_date = (datetime.now()).strftime('%Y-%m-%d')
#
#            fname = "../" + fname
#
#            try:
#                with open(fname, mode='r') as daily_tweets:
#                    df = pd.read_json(path_or_buf=daily_tweets, orient='records', lines=True)
#                    print(df.tail(1))
#                    start_date = df.tail(1)['timestamp']
#
#            except IOError:
#                file = open(fname, 'w')
#            get_tweets(start_date, end_date, company['name'], company['ticker'], "../data/tweets/")
#
#    return 0

if __name__ == "__main__":
    get_tweets('init')  # could take hours