import os
from datetime import time, datetime

import certifi
import pandas as pd
import pymongo
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


class MongoManager:

    def __init__(self):
        self.client = None
        self.db = None

    def open_connection(self):
        self.client = MongoClient(os.environ['MONGO_URL'], tlsCAFile=certifi.where())
        self.db = self.client['Stock-Sentiment']

    def close_connection(self):
        self.client.close()

    def get_tweets(self, ticker, start_date, end_date):
        self.open_connection()
        collection = self.db['Tweets']
        while True:
            cursor = collection.find(
                {
                    "Ticker": ticker,
                    "Datetime": {"$gte": start_date, "$lte": end_date}
                },
            )
            list_cur = list(cursor)
            if len(list_cur) > 0:
                break
            time.sleep(60)

        self.close_connection()
        return pd.DataFrame(list_cur)

    def get_stocks(self, ticker, start_date, end_date):
        self.open_connection()
        collection = self.db['Stocks']
        cursor = collection.find(
            {
                "Ticker": ticker,
                "Date": {"$gte": start_date, "$lte": end_date}
            }
        )
        list_cur = list(cursor)
        self.close_connection()
        return pd.DataFrame(list_cur)

    def last_update_tweets(self, ticker):
        self.open_connection()
        collection = self.db['Tweets']
        cursor = collection.find({'Ticker': ticker}, {'Datetime': 1}).sort('Datetime', -1).limit(1)
        results = list(cursor)
        if len(results) == 0:
            self.close_connection()
            return datetime.utcnow() - relativedelta(days=1)
        else:
            last_date_uploaded = None
            for doc in results:
                last_date_uploaded = doc['Datetime']
            self.close_connection()
            return last_date_uploaded

    def insert_tweets(self, tweet_df):
        self.open_connection()
        collection = self.db['Tweets']
        try:
            collection.insert_many(tweet_df.to_dict('records'))
        except pymongo.errors.BulkWriteError as e:
            print(e.details['writeErrors'])
            panic_list = list(filter(lambda msg: msg['code'] != 11000, e.details['writeErrors']))
            if len(panic_list) > 0:
                print(f"There are not duplicate errors {panic_list}")
        finally:
            self.close_connection()

    def last_update_stocks(self):
        self.open_connection()
        collection = self.db['Stocks']
        cursor = collection.find().sort('Date', -1).limit(1)
        for doc in cursor:
            last_update = doc['Date']
        self.close_connection()
        return last_update

    def insert_stocks(self, stocks_df):
        self.open_connection()
        collection = self.db['Stocks']
        try:
            collection.insert_many(stocks_df.to_dict('records'))
        except pymongo.errors.BulkWriteError as e:
            print(e.details['writeErrors'])
            panic_list = list(filter(lambda msg: msg['code'] != 11000, e.details['writeErrors']))
            if len(panic_list) > 0:
                print(f"There are not duplicate errors {panic_list}")
        finally:
            self.close_connection()

