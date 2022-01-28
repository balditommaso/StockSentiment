import cmd
from datetime import datetime

import pytz
from dateutil.relativedelta import relativedelta

from classification.tweets_classification import classify_tweets, get_daily_polarity
from collecting import stocks_collector
from collecting.mongo_manager import MongoManager
from collecting.tweet_collector import download_tweet
from common.costants import target_company
from preprocessing.tweet_cleaner import filter_tweets
from preprocessing.tweet_weight import set_tweets_weight


class App(cmd.Cmd):
    intro = 'Stock Sentiment Stock Database Updater Launched\n'
    prompt = '>'
    mongoDB = MongoManager()

    def do_exit(self, arg):
        exit(0)

    def do_init(self, arg):
        'Init the Stocks Database'
        # Download stocks data
        start_date = '2021-01-01'
        end_date = '2022-01-24'
        self.update_stocks(start_date, end_date)

    def do_update(self, arg):
        'Update the Stocks Database'
        # Retrieves last date updated
        last_date_uploaded = self.mongoDB.last_update_stocks()
        if last_date_uploaded.strftime('%Y-%m-%d') == datetime.now().strftime('%Y-%m-%d'):
            print("Database Stocks already updated ...")
            return

        # Time zones fix
        start_date = (last_date_uploaded + relativedelta(days=2)).strftime('%Y-%m-%d')
        end_date = (datetime.now() + relativedelta(days=1)).strftime('%Y-%m-%d')
        self.update_stocks(start_date, end_date)

    def update_stocks(self, start_date, end_date):
        for company in target_company:
            stocks_df = stocks_collector.download_stocks(company['ticker'], start_date, end_date)

            # Polarity
            for i, row in stocks_df.iterrows():
                # Download tweets until market closes
                day_before = row['Date'] - relativedelta(days=1)
                start_date_tweets = str(int(datetime(day_before.year, day_before.month, day_before.day,
                                                     21, 0, 0, tzinfo=pytz.utc).timestamp()))

                end_date_tweets = str(int(datetime(row['Date'].year, row['Date'].month, row['Date'].day,
                                                   20, 59, 59, tzinfo=pytz.utc).timestamp()))

                # Collecting
                daily_tweets = download_tweet(company['ticker'], company['name'], start_date_tweets, end_date_tweets)

                # Preprocessing
                daily_tweets_cleaned = filter_tweets(daily_tweets, company['ticker'])
                daily_tweets_weighted = set_tweets_weight(daily_tweets_cleaned)

                # Classification
                daily_tweets_classified = classify_tweets(daily_tweets_weighted)
                polarity = get_daily_polarity(daily_tweets_classified)

                stocks_df.at[i, 'Polarity'] = polarity
                stocks_df.at[i, 'Daily_Tweets'] = int(daily_tweets_classified.shape[0])

            if stocks_df.shape[0] != 0:  # Faster than DataFrame.empty
                self.mongoDB.insert_stocks(stocks_df)
                print("Database Stocks updated ...")
            else:
                print("Database Stocks already updated ...")


if __name__ == '__main__':
    App().cmdloop()