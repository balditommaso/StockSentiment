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
            sntwitter.TwitterSearchScraper(keyword + ' since:' + start_date + ' until:' + end_date).get_items()):

        #counter
        print(i, " ", tweet.date)

        # if tweet.likeCount > tot   ### filter unpopular tweets
        tweets_list.append([tweet.user.username, tweet.user.followersCount, tweet.content, tweet.date,
                            tweet.retweetCount, tweet.likeCount, tweet.replyCount])

    # Creating a dataframe from the tweets list above
    tweets_df = pd.DataFrame(tweets_list, columns=["Account_Name", 'Number_Follower', 'Text', 'Datetime',
                                                   'Number_Retweets', 'Number_Likes', 'Number_Comments'])
    print(tweets_df)

    fname = join(dir_path, 'tweets_' + ticker + '_' + start_date + '_' + end_date + '.json')


    with open(fname, 'w') as f:
        print("Saved Json: ", fname)
        tweets_df.to_json(fname, orient="records", lines=True)
    return fname


if __name__ == "__main__":
    start_date = "2021-01-18"
    end_date = "2022-01-18"
    keyword = "tesla TSLA"
    ticker = 'TSLA'
    dir_path = '../data'
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    get_tweets(start_date, end_date, keyword, ticker, dir_path)