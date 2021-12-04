import json
import investpy as inv
import pandas as pd
from datetime import date


def import_last_month(start_date):
    """
    create a file json with the information about the stocks

    :param start_date: select from which date you want retrieve information
    :return: no return
    """
    TARGET_STOCKS = ['AMZN', 'TSLA', 'GOOG', 'GOOGL', 'AAPL', 'MSFT']
    today = date.today()
    format_day = today.strftime('%d/%m/%Y')
    with open("stocks.json", mode='w', encoding='utf-8') as stocks_json:
        for stock in TARGET_STOCKS:
            df = inv.get_stock_historical_data(stock=stock,
                                               country='United States',
                                               from_date=start_date,
                                               to_date=format_day)
            df.insert(6, 'Stock', stock)
            df.reset_index(inplace=True)
            df.to_json(path_or_buf=stocks_json, orient='records', lines=True, index=True, date_format='iso')


if __name__ == "__main__":
    target_date = input('insert the date for downloading the STOCKS: (dd/mm/yyyy)\n')
    import_last_month(target_date)

