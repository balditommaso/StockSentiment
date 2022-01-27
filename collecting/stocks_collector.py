import yfinance as yf


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


def download_stocks(company_ticker, start_date, end_date):
    ticker = yf.Ticker(company_ticker)
    df = ticker.history(start=start_date, end=end_date)
    df.reset_index(inplace=True)
    df['Ticker'] = company_ticker

    return df
