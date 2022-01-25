import pandas as pd
import requests
import os
from os.path import join
from dotenv import load_dotenv
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from pathlib import Path

from common.costants import target_company

# Load environment variables
load_dotenv()

# Initialize API attributes
finhub_key = os.environ['FINHUB_KEY']


def get_finhub_news(ticker, start_date, end_date):
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
    print("Updating  ", ticker, " news ...")
    max_call = 60
    time_sleep = 60
    nb_request = 0

    news = pd.DataFrame(columns=['Ticker', 'Date', 'Headline', 'Source', 'Summary', ' Url'])

    # Number of days between start_date and end_date
    delta_date = abs((datetime.strptime(start_date, "%Y-%m-%d") - datetime.strptime(end_date, "%Y-%m-%d")).days)
    date = start_date
    date_obj = datetime.strptime(start_date, "%Y-%m-%d")

    data = []
    for item in range(delta_date + 1):
        nb_request += 1
        r = requests.get('https://finnhub.io/api/v1/company-news?symbol=' + ticker + '&from=' + date + '&to=' + date
                         + '&token=' + finhub_key)
        data += r.json()
        date_obj = date_obj + relativedelta(days=1)
        date = date_obj.strftime("%Y-%m-%d")
        if nb_request == (max_call - 1):
            time.sleep(time_sleep)
            nb_request = 0

    for result in data:
        print(result)
        contents = {'Date': result['datetime'],
                    'Headline': result['headline'],
                    'Source': result['source'],
                    'Summary': result['summary'],
                    'Url': result['url']
                    }
        news = news.append(contents, ignore_index=True)
        news.sort_values(['Date'], inplace=True, ascending=False)
    return news