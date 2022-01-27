import joblib
import pandas as pd
import numpy as np

def prepare_stock_data(df):

    # Set date as index
    df['Date'] = df['Date'].astype(str).str.split(' ').str[0]
    df = df.set_index('Date')

    # Add label
    df['Label'] = df.rolling(2).apply(lambda x: x.iloc[1] > x.iloc[0])['Close']

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

    # Drop rows with NaN values
    df.dropna(inplace=True)

    return df

def predict_stock_trend(stock_data_with_polarity):
    # Classifying
    clf = joblib.load('model/stock_trend_predictor.pkl')

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

    prediction = clf.predict(stock_data_with_polarity[predictors].values)

    return prediction