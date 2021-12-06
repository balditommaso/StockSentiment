# pip3 install git+https://github.com/JustAnotherArchivist/snscrape.git
import snscrape.modules.twitter as sntwitter
import pandas as pd
from pathlib import Path
from os.path import join


def get_tweets(start_date, end_date, keyword, ticker, dir_path):
    """

    :param start_date:
    :param end_date:
    :param keyword:
    :param dir_path:
    :return:
    """
    tweets_list = []

    for i, tweet in enumerate(
            sntwitter.TwitterSearchScraper('TSLA tesla since:2021-11-05 until:2021-12-05').get_items()):

        #counter
        print(i, " ", tweet.date)

       # if tweet.likeCount > tot   ### filter unpopular tweets
        tweets_list.append([tweet.id, tweet.url, tweet.user.username, tweet.content, tweet.date, tweet.retweetCount,
                            tweet.likeCount, tweet.replyCount])

    # Creating a dataframe from the tweets list above
    tweets_df = pd.DataFrame(tweets_list, columns=['Tweet_ID', 'URL', "Account_Name", 'Text', 'Datetime',
                                                   'Number_Retweets', 'Number_Likes', 'Number_Comments'])
    print(tweets_df)

    fname = join(dir_path, 'tweets_' + ticker + '_' + start_date + '_' + end_date + '.json')

    with open(fname, 'w') as f:
        print("Saved Json: ", fname)
        tweets_df.to_json(fname, orient="records", lines=True)


if __name__ == "__main__":
    start_date = "2020-12-06"
    end_date = "2021-12-05"
    keyword = "tesla OR TSLA"
    ticker = 'TSLA'
    dir_path = '../data'
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    get_tweets(start_date, end_date, keyword, ticker, dir_path)