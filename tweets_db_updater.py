import signal
import time
from datetime import datetime
import threading
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient

from collecting.tweet_collector import download_tweet
from common.costants import target_company

client = MongoClient('mongodb+srv://root:root@cluster0.wvzn3.mongodb.net/'
                     'Stock-Sentiment?retryWrites=true&w=majority')
db = client['Stock-Sentiment']
stored_tweets = db['Tweets']

last_updates = []


def check_last_insert():
    for company in target_company:
        cursor = stored_tweets.find({'Ticker': company['ticker']}, {'Datetime': 1}).sort('Datetime', -1).limit(1)
        for doc in cursor:
            last_date_uploaded = doc['Datetime']
        if len(list(cursor)) == 0:
            last_updates.append({'ticker': company['ticker'], 'date': (datetime.utcnow() - relativedelta(days=1))})
        else:
            for update in last_updates:
                if update['ticker'] == company['ticker']:
                    update['date'] = last_date_uploaded
                    return
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
            start_date = str(int((last_update + relativedelta(seconds=1)).timestamp()))
            today = datetime.utcnow()
            end_date = str(int(today.timestamp()))
            set_last_update(company['ticker'], today)
            new_tweets = download_tweet(company['ticker'], company['name'], start_date, end_date)
            if new_tweets.shape[0] > 0:
                stored_tweets.insert_many(new_tweets.to_dict('records'))
        time.sleep(60)  # wait 1 minute


signal.signal(signal.SIGTERM, handle_stop)


if __name__ == '__main__':
    check_last_insert()
    stop_event = threading.Event()
    updater = threading.Thread(target=insert_new_tweets, args=(0, stop_event))
    updater.start()
    while True:
        try:
            print(last_updates)
            time.sleep(60)
        except KeyboardInterrupt:
            handle_stop()

