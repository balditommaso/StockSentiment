import yfinance as yf
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

from common.costants import target_company


def update_stocks(arg):
    target_company.append({'name': "S&P 500", 'ticker': "SPY"})
    for company in target_company:
        fname = "data/historical_data/" + company['ticker'] + ".json"
        if arg == 'init':
            start_date = "2021-01-18"
            end_date = "2022-01-18"
            fname = "../" + fname
            mode = 'w'
        elif arg == 'update':
            end_date = (datetime.now() + relativedelta(days=1)).strftime('%Y-%m-%d')
            with open(fname, mode='r') as saved_stocks:
                df = pd.read_json(path_or_buf=saved_stocks, orient='records', lines=True)
            last_insert = df.tail(1)['Date'].values[0]
            start_date = pd.to_datetime(str(last_insert))
            start_date = (start_date + relativedelta(days=1)).strftime('%Y-%m-%d')
            mode = 'a'

        ticker = yf.Ticker(company['ticker'])
        hist = ticker.history(start=start_date, end=end_date)
        hist.reset_index(inplace=True)
        with open(fname, mode=mode, encoding='utf-8') as stocks_json:
            hist.to_json(path_or_buf=stocks_json, orient='records', lines=True, index=True, date_format='iso')
        # target_company.remove({'name': "S&P 500", 'ticker': "SPY"})

# init the storage
if __name__ == "__main__":
    update_stocks('init')