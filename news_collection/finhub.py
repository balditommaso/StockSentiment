import pandas as pd
import requests
import os
from os.path import join
from dotenv import load_dotenv
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from pathlib import Path

load_dotenv()

def get_finhub_news(start_date, end_date, tickers, dir_path):
    """
    Method that uses FINHUB API for retrieving all the news published between start_date and end_date of all the tickers
    specified in tickers and saves the information in .json in dir_path

    :param start_date: string
    :param end_date: string
    :param tickers: list
        List of strings which contains the tickers of which we want to obtain information
    :param dir_path: string
        Path where the .json file will be saved
    """

    # Date tests
    if datetime.strptime(start_date, "%Y-%m-%d") > datetime.strptime(end_date, "%Y-%m-%d"):
        print("'start_date' is after 'end_date'")
        return -1

    if datetime.strptime(start_date, "%Y-%m-%d") <= (datetime.now() - relativedelta(years=1)):
        print("'start_date' is older than 1 year. It doesn't work with the free version of FinHub")
        return -1

    # Initialize API attributes
    max_call = 60
    time_sleep = 60
    nb_request = 0
    finhub_key = os.environ['FINHUB_KEY']

    for ticker in tickers:
        print("Processing ", ticker)
        news = pd.DataFrame(columns=['ticker', 'datetime', 'headline', 'source', 'summary'])

        # Number of days between start_date and end_date
        delta_date = abs((datetime.strptime(start_date, "%Y-%m-%d") - datetime.strptime(end_date, "%Y-%m-%d")).days)

        date = start_date
        date_obj = datetime.strptime(start_date, "%Y-%m-%d")

        data = []
        for item in range(delta_date + 1):
            print("Processing ", date)
            nb_request += 1
            r = requests.get('https://finnhub.io/api/v1/company-news?symbol=' + ticker + '&from=' + date + '&to=' + date
                             + '&token=' + finhub_key)
            data += r.json()
            print(data)
            date_obj = date_obj + relativedelta(days=1)
            date = date_obj.strftime("%Y-%m-%d")
            if nb_request == (max_call - 1):
                time.sleep(time_sleep)
                nb_request = 0

        for result in data:
            contents = {'ticker' : result['related'],
                        'datetime': result['datetime'],
                        'headline': result['headline'],
                        'source': result['source'],
                        'summary': result['summary']
                        }
            news = news.append(contents, ignore_index=True)

        fname = join(dir_path, ticker + '_' + start_date + '_' + end_date + '.json')

        with open(fname, 'w') as f:
            print("Saved Json: ", fname)
            news.to_json(fname, orient="records", lines=True)


if __name__ == "__main__":
    start_date = "2020-12-05"
    end_date = "2021-12-03"
    #tickers = get_S&P500_tickers.get_tickers()
    tickers = ['TSLA']
    dir_path = '../data'
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    get_finhub_news(start_date, end_date, tickers, dir_path)