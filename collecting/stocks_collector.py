import investpy as inv
import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from common.costants import target_company


def import_stocks_data(start_date):
    """
    create a file json with the information about the stocks

    :param start_date: select from which date you want retrieve information
    :return: no return
    """
    today = date.today()
    format_day = today.strftime('%d/%m/%Y')
    for stock in target_company:
        df = inv.get_stock_historical_data(stock=stock['ticker'],
                                           country='United States',
                                           from_date=start_date,
                                           to_date=format_day)
        df.insert(6, 'Stock', stock['ticker'])
        df.reset_index(inplace=True)
        with open("../data/historical_data/" + stock['ticker'] + ".json", mode='w', encoding='utf-8') as stocks_json:
            df.to_json(path_or_buf=stocks_json, orient='records', lines=True, index=True, date_format='iso')


def update_stocks():
    """
    function to update stocks information when the app
    starts.
    Attention: file path are referenced to the main application
    :return:
    """
    # take the current day
    today = datetime.now() - relativedelta(days=1)
    end_date = today.strftime('%d/%m/%Y')
    # take the last updated day
    for stock in target_company:
        fname = "data/historical_data/" + stock['ticker'] + ".json"
        with open(fname, mode='r') as saveded_stocks:
            df = pd.read_json(path_or_buf=saveded_stocks, orient='records', lines=True)
        last_insert = df.tail(1)['Date'].values[0]
        start_date = pd.to_datetime(str(last_insert))
        start_date = (start_date + relativedelta(days=1)).strftime('%d/%m/%Y')
        # update with new data
        try:
            updated_stocks = inv.get_stock_historical_data(stock=stock['ticker'],
                                                           country='United States',
                                                           from_date=start_date,
                                                           to_date=end_date)
        except:
            print(stock['ticker'], ": historical data updated")
            continue
        updated_stocks.insert(6, 'Stock', stock['ticker'])
        updated_stocks.reset_index(inplace=True)
        with open("data/historical_data/" + stock['ticker'] + ".json", mode='a', encoding='utf-8') as stocks_json:
            updated_stocks.to_json(path_or_buf=stocks_json, orient='records', lines=True, index=True, date_format='iso')


def import_index_data(start_date):
    """
    create a file json with the historical data of S&P500 index

    :param start_date: date from which date we want retrieve information
    :return: no return
    """
    today = date.today()
    format_day = today.strftime('%d/%m/%Y')

    df = inv.get_index_historical_data(index='S&P 500',
                                            country='United States',
                                            from_date=start_date,
                                            to_date=format_day)
    df.reset_index(inplace=True)
    with open("../data/historical_data/S&P500.json", mode='w', encoding='utf-8') as sp500_json:
        df.to_json(path_or_buf=sp500_json, orient='records', lines=True, index=True, date_format='iso')


if __name__ == "__main__":
    #target_date = input('insert the date for downloading the STOCKS: (dd/mm/yyyy)\n')
    start_date = "1/1/2017"
    #import_stocks_data(start_date)
    import_index_data(start_date)
