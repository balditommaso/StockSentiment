import joblib
import pandas as pd
import numpy as np


def prepare_stock_data(df, avg_polarity):

    # Drop unused columns
    df.drop(columns=["Date", "Ticker"], inplace=True)

    # Add a new row with daily current sentiment
    row = {'Polarity': avg_polarity}

    df = df.append(row, ignore_index=True)

    # Shift one day, we can not use the future to predict the past
    df[['Open', 'High', 'Low', 'Close', 'Volume']] = df[['Open', 'High', 'Low', 'Close', 'Volume']].shift(1)

    df = df.rename(columns={'Open': 'Prev Open', 'High': 'Prev High', 'Low': 'Prev Low',
                            'Close': 'Prev Close', 'Volume': 'Prev Volume', })

    # Compute Exponential Mobile Average (EMA) for stock price daily increments
    delta = df['Prev Close'] - df['Prev Open']
    df['10 Days Incr EMA'] = np.round(delta.copy().ewm(span=10, adjust=False).mean(), decimals=3)
    df['5 Days Incr EMA'] = np.round(delta.copy().ewm(span=5, adjust=False).mean(), decimals=3)
    df['3 Days Incr EMA'] = np.round(delta.copy().ewm(span=3, adjust=False).mean(), decimals=3)

    # Compute Exponential Mobile Average (EMA) for stock polarity
    df['10 Days Pol EMA'] = np.round(df['Polarity'].copy().ewm(span=10, adjust=False).mean(), decimals=3)
    df['5 Days Pol EMA'] = np.round(df['Polarity'].copy().ewm(span=5, adjust=False).mean(), decimals=3)
    df['3 Days Pol EMA'] = np.round(df['Polarity'].copy().ewm(span=3, adjust=False).mean(), decimals=3)

    return df.tail(1)

def predict_stock_trend(stock_data_with_polarity, avg_polarity):
    # Classifying
    clf = joblib.load('../model/stock_trend_predictor.pkl')

    today_data = prepare_stock_data(stock_data_with_polarity, avg_polarity)
    # print(today_data)

    predictors = ['Prev Close',
                  'Prev Volume',
                  'Polarity',
                  '10 Days Incr EMA',
                  '5 Days Incr EMA',
                  '3 Days Incr EMA',
                  '10 Days Pol EMA',
                  '5 Days Pol EMA',
                  '3 Days Pol EMA'
                  ]

    prediction = clf.predict(today_data[predictors])

    return prediction


if __name__ == "__main__":
    df = pd.read_csv('../training/data/AMZN_stock_data_with_polarity.csv')
    df = df.tail(100)
    pred = predict_stock_trend(df, 7000.6)

    print(pred)