import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

from common.costants import target_company


def update_stocks(arg):

    for company in target_company:
        fname = "../data/historical_data/" + company['ticker'] + ".json"
        if arg == 'init':
            start_date = "2017-01-18"
            end_date = "2022-01-18"
            mode = 'w'
        elif arg == 'update':
            end_date = (datetime.now() + relativedelta(days=1)).strftime('%Y-%m-%d')

            # Retrieve the date of the last update
            with open(fname, mode='r') as saved_stocks:
                df = pd.read_json(path_or_buf=saved_stocks, orient='records', lines=True)
            df['Date'] = pd.to_datetime(df['Date'])
            last_insert = df['Date'].max()
            start_date = (last_insert + relativedelta(days=1)).strftime('%Y-%m-%d')
            mode = 'a'

        stocks_df = download_stocks(company['ticker'], start_date, end_date)

        if stocks_df.shape[0] != 0:  # Faster than DataFrame.empty
            with open(fname, mode=mode, encoding='utf-8') as stocks_json:
                stocks_df.to_json(path_or_buf=stocks_json, orient='records', lines=True, index=True, date_format='iso')


def get_live_data(stock):
    df = yf.download(tickers=stock, period='1d', interval='1m')

    # Newest data
    actual_close = df.tail(1)['Close'].values[0]

    # Compute change and pct change
    df = yf.download(tickers=stock, period='2d')
    yesterday_close = df.head(1)['Close'].values[0]
    change = actual_close - yesterday_close
    pct_change = actual_close / yesterday_close * 100

    return actual_close, change, pct_change


def download_stocks(ticker, start_date, end_date):
    ticker = yf.Ticker(ticker)
    hist = ticker.history(start=start_date, end=end_date)
    hist.reset_index(inplace=True)
    return hist


# init the storage
if __name__ == "__main__":
    #update_stocks('init')
    #update_stocks('update')
    get_live_data('AAPL')