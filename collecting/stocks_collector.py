import json
import investpy as inv
import pandas as pd
from datetime import date


def import_stocks_data(start_date):
    """
    create a file json with the information about the stocks

    :param start_date: select from which date you want retrieve information
    :return: no return
    """
    TARGET_STOCKS = ['AMZN', 'TSLA', 'GOOGL', 'AAPL', 'MSFT']
    today = date.today()
    format_day = today.strftime('%d/%m/%Y')
    for stock in TARGET_STOCKS:
        df = inv.get_stock_historical_data(stock=stock,
                                           country='United States',
                                           from_date=start_date,
                                           to_date=format_day)
        df.insert(6, 'Stock', stock)
        df.reset_index(inplace=True)
        with open("../data/historical_data/" + stock + ".json", mode='w', encoding='utf-8') as stocks_json:
            df.to_json(path_or_buf=stocks_json, orient='records', lines=True, index=True, date_format='iso')


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
    with open("../data/historical_data/s&p500.json", mode='w', encoding='utf-8') as sp500_json:
        df.to_json(path_or_buf=sp500_json, orient='records', lines=True, index=True, date_format='iso')

if __name__ == "__main__":
    #target_date = input('insert the date for downloading the STOCKS: (dd/mm/yyyy)\n')
    start_date = "1/1/2021"
    import_stocks_data(start_date)
    import_index_data(start_date)
