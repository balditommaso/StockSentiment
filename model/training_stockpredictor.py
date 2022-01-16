import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Lasso, ElasticNet
from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score, mean_squared_error
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.model_selection import TimeSeriesSplit
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor


def train():
    df = pd.read_json('../data/historical_data/AMZN.json', lines=True)
    df1 = pd.read_json('../data/historical_data/s&p500.json', lines=True)

    # Rename columns
    df = df.rename(columns={'Open': 'Stock Open', 'Close': 'Stock Close'})
    df1 = df1.rename(columns={'Open': 'S&P 500 Open', 'Close': 'S&P 500 Close'})

    # Join dataframes
    df = pd.merge(df[['Date', 'Stock Open', 'Stock Close']], df1[['Date', 'S&P 500 Open', 'S&P 500 Close']], on='Date',
                  how='outer')

    # Add previous day close price
    df['Stock Close Prev'] = df['Stock Close'].shift(1)
    df['S&P 500 Close Prev'] = df['S&P 500 Close'].shift(1)

    # Compute Exponential Mobile Average (EMA) for stock values and index values
    stock_value_ema = df['Stock Close'].copy().ewm(span=10, adjust=False).mean()
    df['Stock Close EMA'] = np.round(stock_value_ema, decimals=3)
    sp500_ema = df['S&P 500 Close'].copy().ewm(span=10, adjust=False).mean()
    df['S&P 500 Close EMA'] = np.round(sp500_ema, decimals=3)

    # Shift EMAs in order to have the previous days trend along with today close value
    df['Stock Close EMA'] = df['Stock Close EMA'].shift(1)
    df['S&P 500 Close EMA'] = df['S&P 500 Close EMA'].shift(1)

    # Add sentiment analysis

    # Drop rows with NaN values
    df.dropna(inplace=True)

    # Re order columns
    df = df[['Date', 'Stock Open', 'Stock Close', 'Stock Close Prev', 'Stock Close EMA',
            'S&P 500 Open', 'S&P 500 Close Prev', 'S&P 500 Close EMA']]

    # Save final dataset
    with open("stock_prediction_dataset.json", mode='w', encoding='utf-8') as final_dataset_json:
        df.to_json(path_or_buf=final_dataset_json, orient='records', lines=True, index=True, date_format='iso')

    x_train, x_test, y_train, y_test = train_test_split(df[['Stock Open', 'Stock Close Prev', 'Stock Close EMA',
                                                            'S&P 500 Open', 'S&P 500 Close Prev', 'S&P 500 Close EMA']],
                                                        df[['Stock Close']], test_size=.2,
                                                        shuffle=False, random_state=0)

    date_test = df.loc[:np.floor(df.shape[0] * 0.2) + 1, ['Date']]

    """
    # Test options and evaluation metric
    num_folds = 10
    seed = 7
    scoring = "r2"

    # Spot-Check Algorithms
    models = []
    models.append((' LR ', LinearRegression()))
    models.append((' LASSO ', Lasso()))
    models.append((' EN ', ElasticNet()))
    models.append((' KNN ', KNeighborsRegressor()))
    models.append((' CART ', DecisionTreeRegressor()))
    models.append((' SVR ', SVR()))

    # evaluate each model in turn
    results = []
    names = []
    for name, model in models:
        kfold = KFold(n_splits=num_folds, random_state=seed, shuffle=True)
        cv_results = cross_val_score(model, x_train, y_train, cv=kfold, scoring=scoring)
        # print(cv_results)
        results.append(cv_results)
        names.append(name)
        msg = "%s: %f (%f)" % (name, cv_results.mean(), cv_results.std())
        print(msg)

    """
    # Create Regression Model
    clf = LinearRegression()
    #clf = Lasso(tol=7.939e+02)
    #clf = ElasticNet(tol=5.293e+02)
    #clf = KNeighborsRegressor()
    #clf = DecisionTreeRegressor()
    #clf = RandomForestRegressor(max_depth=2, random_state=0)
    #clf = SVR() # does not work

    # Train the model
    clf.fit(x_train, y_train)

    # Use model to make predictions
    y_pred = clf.predict(x_test)

    # Printout relevant metrics
    print("Mean Absolute Error:", mean_absolute_error(y_test, y_pred))
    print("Mean Squared Error:", mean_squared_error(y_test, y_pred))
    print("R^2:", r2_score(y_test, y_pred))

    plt.xticks(rotation=45)
    plt.plot_date(date_test, y_test, fmt='b-', xdate=True, ydate=False, label='Real value')
    plt.plot_date(date_test, y_pred, fmt='r-', xdate=True, ydate=False, label='Predicted value')
    plt.legend(loc='upper center')
    plt.ylabel('Close prices')
    plt.title('Amazon (NASDAQ:AMZN)')
    #plt.show()


train()
