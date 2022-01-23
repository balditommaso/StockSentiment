import cmd
from datetime import datetime

import joblib
import pandas as pd
import pytz
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient

import collecting.stocks_collector
from collecting import stocks_collector
from collecting.tweet_collector import download_tweet
from common.costants import target_company
from preprocessing.tweet_cleaner import filter_tweets
from preprocessing.tweet_weight import set_tweets_weight


class App(cmd.Cmd):
    intro = 'Stock Value Predictor Database updater'
    prompt = '>'
    mongo_client = MongoClient('localhost', 27017)

    def do_init(self, arg):
        'Init the database'

        self.mongo_client.drop_database('Stock-Value-Predictor')
        db = self.mongo_client['Stock-Value-Predictor']

        # Download stocks data
        start_date = '2021-01-18'
        end_date = datetime.now().strftime("%Y-%m-%d")
        df = pd.DataFrame()

        for company in target_company:
            df = df.append(stocks_collector.download_stocks(company['ticker'], start_date, end_date))



        db['Stocks'].insert_many(df.to_dict("records"))

    def do_update(self, arg):
        print("Updating database stocks ...")

        db = self.mongo_client['Stock-Value-Predictor']

        doc = db['Stocks'].find().sort('Date', -1).limit(1)

        for x in doc:
            last_date_uploaded = x['Date']

        if last_date_uploaded.strftime('%Y-%m-%d') == datetime.now().strftime('%Y-%m-%d'):
            print("Database Stocks already updated ...")
            return

        # Time zones fix
        start_date = (last_date_uploaded + relativedelta(days=2)).strftime('%Y-%m-%d')
        end_date = (datetime.now() + relativedelta(days=1)).strftime('%Y-%m-%d')

        for company in target_company:
            df = stocks_collector.download_stocks(company['ticker'], start_date, end_date)

            #Polarity
            for i, row in df.iterrows():
                # Download tweets until market closes
                start_date_tweets = str(int(datetime(row['Date'].year, row['Date'].month, row['Date'].day - 1,
                                                     16, 0, 0,
                                                     tzinfo=pytz.utc).timestamp()))

                end_date_tweets = str(int(datetime(row['Date'].year, row['Date'].month, row['Date'].day,
                                                     15, 59, 59,
                                                     tzinfo=pytz.utc).timestamp()))

                # Collecting
                daily_tweets = download_tweet(company['ticker'], company['name'], start_date_tweets, end_date_tweets)

                # Preprocessing
                daily_tweets_cleaned = filter_tweets(daily_tweets, company['ticker'])
                daily_tweets_weghted = set_tweets_weight(daily_tweets_cleaned)

                # Classifying
                clf = joblib.load('model/sentiment_classifier.pkl')
                prediction = clf.predict(daily_tweets_weghted["Text"].values)
                daily_tweets_weghted['Polarity'] = prediction

                # Summarize polarity
                sum = 0
                for j, tweet in daily_tweets_weghted.iterrows():
                    if tweet['Polarity'] == 'positive':
                        sum = sum + tweet['Weight']
                    elif tweet['Polarity'] == 'Negative':
                        sum = sum - tweet['Weight']

                avg_polarity = sum / daily_tweets_weghted.shape[0]

                df.at[i, 'Polarity'] = avg_polarity

        if df.shape[0] != 0:  # Faster than DataFrame.empty
            db['Stocks'].insert_many(df.to_dict("records"))
            print("Database Stocks updated ...")
        else:
            print("Database Stocks already updated ...")

if __name__ == '__main__':
    App().cmdloop()