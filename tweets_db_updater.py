import signal
import time
import certifi
from datetime import datetime
import threading

import pymongo.errors
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient

from collecting.mongo_manager import MongoManager
from collecting.tweet_collector import download_tweet
from common.costants import target_company

mongoDB = MongoManager()

last_updates = []


def init():
    for company in target_company:
        result = mongoDB.last_update_tweets(company['ticker'])
        last_updates.append({'ticker': company['ticker'], 'date': result})


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
    exit(0)


def insert_new_tweets(args, stop_event):
    while not stop_event.is_set():
        for company in target_company:
            last_update = get_last_update(company['ticker'])
            # snscrape remove 1 hour from the start date
            start_date = (int((last_update + relativedelta(hours=1, seconds=1)).timestamp()))
            today = datetime.utcnow()
            end_date = (int(today.timestamp()))
            set_last_update(company['ticker'], today)
            new_tweets = download_tweet(company['ticker'], company['name'], str(start_date), str(end_date))
            if new_tweets.shape[0] > 0:
                mongoDB.insert_tweets(new_tweets)
        time.sleep(60)  # wait 1 minute


signal.signal(signal.SIGTERM, handle_stop)


if __name__ == '__main__':
    init()
    stop_event = threading.Event()
    updater = threading.Thread(target=insert_new_tweets, args=(0, stop_event))
    updater.start()
    while True:
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            handle_stop()

