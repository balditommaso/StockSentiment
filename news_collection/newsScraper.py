import time
from random import randint
from urllib.request import urlopen, Request

import dateutil
from bs4 import BeautifulSoup
import requests, urllib.parse, lxml
import json
import requests
from os import makedirs
from os.path import join, exists
from dotenv import load_dotenv
import datetime
from datetime import date, timedelta
import os
import pandas as pd

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}

load_dotenv()

from GoogleNews import GoogleNews
def compile_google_news(start_date='2020-11-01', end_date='2020-11-30'):
    ARTICLES_DIR = join('../data', 'Google-News')
    makedirs(ARTICLES_DIR, exist_ok=True)

    googlenews = GoogleNews()
    googlenews.set_lang('en')
    googlenews.set_time_range(start_date, end_date)
    googlenews.set_encode('utf-8')

    googlenews.get_news('TESLA')
    results = googlenews.results(sort=True)

    news = pd.DataFrame(columns=['source', 'date', 'headline', 'text'])

    for result in results:
        contents = {'source' : result['site'],
                    'date' : result['date'], # da convertire in %YYYY-mm-dd
                    'headline' : result['title']
                    }
        news = news.append(contents, ignore_index=True)

    fname = join(ARTICLES_DIR, start_date + '_' + end_date + '.json')

    with open(fname, 'w') as f:
        print("Saved Json: ", fname)
        news.to_json(fname, orient="records", lines=True)

    googlenews.clear()


def compile_guardian(start_date='2021-11-01', end_date='2021-11-30'):
    ARTICLES_DIR = join('../data', 'The-Guardian')
    makedirs(ARTICLES_DIR, exist_ok=True)

    theguardian_url = 'http://content.guardianapis.com/search'
    MY_API_KEY = os.environ['The_Guardian_Key']
    my_params = {
        'q': 'tesla OR (elon AND musk)',
        'from-date': start_date,
        'to-date': end_date,
        'order-by': "newest",
        'show-fields': 'all',
        'page-size': 200,
        'api-key': MY_API_KEY
    }

    news = pd.DataFrame(columns=['source', 'date', 'headline', 'text'])

    resp = requests.get(theguardian_url, my_params)
    data = resp.json()

    for result in data['response']['results']:
        contents = {'source' : 'The Guardian',
                    'date' : result['webPublicationDate'],
                    'headline' : result['webTitle'],
                    'text' : result['fields']['bodyText']
                    }
        news = news.append(contents, ignore_index=True)

    fname = join(ARTICLES_DIR, start_date + '_' + end_date + '.json')

    with open(fname, 'w') as f:
        print("Saved Json: ", fname)
        news.to_json(fname, orient="records", lines=True)


def compile_newyorktimes(start_date="2021-11-01", end_date="2021-11-30"):
    ARTICLES_DIR = join('../data', 'New-York-Times')
    makedirs(ARTICLES_DIR, exist_ok=True)

    newyorktimes_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json?"
    MY_API_KEY = os.environ['New_York_Times_Key']
    my_params = {
        'q': 'tesla OR (elon AND musk)',
        'begin_date': start_date,
        'end_date': end_date,
        'order-by': "newest",
        'show-fields': 'all',
        'page-size': 200,
        'api-key': MY_API_KEY
    }

    news = pd.DataFrame(columns=['source', 'date', 'headline', 'text'])

    resp = requests.get(newyorktimes_url, my_params)
    data = resp.json()

    for result in data['response']['docs']:
        contents = {'source' : 'New York Times',
                    'date' : result['pub_date'],
                    'headline' : result['headline']['main'],
                    'text' : result['abstract']
                    }
        news = news.append(contents, ignore_index=True)

    fname = join(ARTICLES_DIR, start_date + '_' + end_date + '.json')

    with open(fname, 'w') as f:
        print("Saved Json: ", fname)
        news.to_json(fname, orient="records", lines=True)


if __name__ == "__main__":
    compile_google_news()
    compile_guardian()
    compile_newyorktimes()


"""
tickers = ['AMZN', 'TSLA', 'GOOG', 'GOOGL', 'AAPL', 'MSFT']
#https://github.com/bck1990/stock_news_sentiment_analysis
def compile_finviz(start_date, end_date):
    finviz_url = 'https://finviz.com/quote.ashx?t='
    news_tables = {}

    for ticker in tickers:
        url = finviz_url + ticker
        req = Request(url=url,headers=headers)
        response = urlopen(req)
        # Read the contents of the file into 'html'
        html = BeautifulSoup(response, "html.parser")
        # Find 'news-table' in the Soup and load it into 'news_table'
        news_table = html.find(id='news-table')
        # Add the table to our dictionary
        news_tables[ticker] = news_table

    parsed_news = []

    # Iterate through the news
    for file_name, news_table in news_tables.items():
        # Iterate through all tr tags in 'news_table'
        for x in news_table.findAll('tr'):
            # read the text from each tr tag into text
            # get text from a only
            text = x.a.get_text()
            # splite text in the td tag into a list
            date_scrape = x.td.text.split()
            # if the length of 'date_scrape' is 1, load 'time' as the only element

            if len(date_scrape) == 1:
                time = date_scrape[0]

            # else load 'date' as the 1st element and 'time' as the second
            else:
                date = date_scrape[0]
                time = date_scrape[1]
            # Extract the ticker from the file name, get the string up to the 1st '_'
            ticker = file_name.split('_')[0]

            # Append ticker, date, time and headline as a list to the 'parsed_news' list
            parsed_news.append([ticker, date, time, text])

    return parsed_news

#compile_finviz(0,0)

from newsapi import NewsApiClient
# max one month
def compile_newsapi(start_date, end_date):
    ARTICLES_DIR = join('../data', 'News-API')
    makedirs(ARTICLES_DIR, exist_ok=True)

    api = NewsApiClient(os.environ['News_API_Key'])
    data = api.get_everything(
                        q='tesla OR (elon AND musk)',
                        from_param=start_date,
                        to=end_date
    )

    fname = join(ARTICLES_DIR, 'prova.json')
    with open(fname, 'w') as f:
        print("Writing to", fname)
        # re-serialize it for pretty indentation
        f.write(json.dumps(data, indent=2))

#compile_newsapi("2021-11-03", "2021-12-02")
"""