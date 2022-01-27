# pip3 install git+https://github.com/JustAnotherArchivist/snscrape.git
import snscrape.modules.twitter as sntwitter
import pandas as pd


def download_tweet(ticker, name, start_date, end_date):
    """
    Method that uses snscrape API to retrieve all the tweets published between start_date and end_date containing
    keywords ticker and name.

    :param ticker: string
    :param name: string
    :param start_date: string
    :param end_date: string
    """
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
