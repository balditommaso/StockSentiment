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
        cursor = stored_tweets.find({'Ticker': company['ticker']}, {'Date': 1}).sort('Date', -1).limit(1)
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


def set_last_update(ticker):
    for update in last_updates:
        if update['ticker'] == ticker:
            update['date'] = datetime.utcnow()


def insert_new_tweets(args):
    t = threading.current_thread()
    while getattr(t, 'do_run', True):
        time.sleep(60)      # wait 1 minute
        for company in target_company:
            last_update = get_last_update(company['ticker'])
            start_date = str(int((last_update + relativedelta(seconds=1)).timestamp()))
            end_date = str(int(datetime.utcnow().timestamp()))
            set_last_update(company['ticker'])
            new_tweets = download_tweet(company['ticker'], company['name'], start_date, end_date)
            if new_tweets.shape[0] > 0:
                stored_tweets.insert_many(new_tweets.to_dict('records'))


if __name__ == '__main__':
    check_last_insert()
    updater = threading.Thread(target=insert_new_tweets, args=(0,))
    updater.start()
    while True:
        print(last_updates)
        command = input('Write stop to block the daemon:\n>')
        if command == 'stop':
            updater.do_run = False