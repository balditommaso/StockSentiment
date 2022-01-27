import signal
import time
import certifi
from datetime import datetime
import threading

import pymongo.errors
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient

from collecting.tweet_collector import download_tweet
from common.costants import target_company

client = MongoClient(
    'mongodb+srv://root:root@cluster0.wvzn3.mongodb.net/Stock-Sentiment?retryWrites=true&w=majority',
    tlsCAFile=certifi.where()
)
db = client['Stock-Sentiment']
stored_tweets = db['Tweets']

last_updates = []


def init():
    for company in target_company:
        cursor = stored_tweets.find({'Ticker': company['ticker']}, {'Datetime': 1}).sort('Datetime', -1).limit(1)
        results = list(cursor)
        if len(results) == 0:
            last_updates.append({'ticker': company['ticker'], 'date': (datetime.utcnow() - relativedelta(days=1))})
        else:
            last_date_uploaded = None
            for doc in results:
                last_date_uploaded = doc['Datetime']
            last_updates.append({'ticker': company['ticker'], 'date': last_date_uploaded})


def get_last_update(ticker):
    for update in last_updates:
        if update['ticker'] == ticker:
            return update['date']


def set_last_update(ticker, today):
    for update in last_updates:
        if update['ticker'] == ticker:
            update['date'] = today


def handle_stop():
    stop_event.set()
    updater.join()
    client.close()
    exit(0)


def insert_new_tweets(args, stop_event):
    while not stop_event.is_set():
        for company in target_company:
            last_update = get_last_update(company['ticker'])
            print(company['ticker'], last_update)
            # snscrape remove 1 hour from the start date
            start_date = (int((last_update + relativedelta(hours=1, seconds=1)).timestamp()))
            today = datetime.utcnow()
            end_date = (int(today.timestamp()))
            print(datetime.fromtimestamp(start_date), datetime.fromtimestamp(end_date))
            set_last_update(company['ticker'], today)
            new_tweets = download_tweet(company['ticker'], company['name'], str(start_date), str(end_date))
            print(new_tweets)
            if new_tweets.shape[0] > 0:
                try:
                    print(stored_tweets.insert_many(new_tweets.to_dict('records')))
                except pymongo.errors.BulkWriteError as e:
                    print(e.details['writeErrors'])
                    panic_list = list(filter(lambda msg: msg['code'] != 11000, e.details['writeErrors']))
                    if len(panic_list) > 0:
                        print(f"There are not duplicate errors {panic_list}")
        time.sleep(60)  # wait 1 minute


signal.signal(signal.SIGTERM, handle_stop)


if __name__ == '__main__':
    init()
    stop_event = threading.Event()
    updater = threading.Thread(target=insert_new_tweets, args=(0, stop_event))
    updater.start()
    while True:
        try:
            print(last_updates)
            time.sleep(60)
        except KeyboardInterrupt:
            handle_stop()

