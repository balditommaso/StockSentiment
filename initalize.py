from datetime import datetime

import pandas as pd

if __name__ == '__main__':
    fname = 'data/tweets/tweets_AAPL.json'
    with open(fname, mode='r') as file:
        tweets = pd.read_json(path_or_buf=file, orient='records', lines=True)
    tweets['Datetime'] = tweets['Datetime'].dt.strftime('%m-%d-%y')
    print(tweets.head()['Datetime'])