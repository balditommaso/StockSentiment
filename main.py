import json
import time
import dash
import joblib
import numpy as np
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

import common.costants as const
from preprocessing.tweet_cleaner import filter_tweets, select_only_keyword, select_only_english, remove_special_char
from collecting.stocks_collector import update_stocks
from collecting.tweet_collector import get_tweets

stylesheet = ['./assets/style.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

app.layout = html.Div([
    # create a loading page
    update_stocks('update'),
    get_tweets('update'),
    html.Div(
        id="container",
        children=[
            html.Div(
                className="app-header",
                children=[
                    html.Div('Stock Value Predictor', className="title"),
                    html.Label("your best friend for investments")
                ]
            ),
            html.Hr(),
            html.Div(
                className="set-option",
                children=[
                    dcc.Dropdown(
                        id='select-stock',
                        placeholder='Select Stock',
                        options=[{'label': i['name'], 'value': i['ticker']} for i in const.target_company],
                        value=None
                    ),
                ]
            ),
            html.Div(
                id='stocks-view',
                children=[
                    dcc.Slider(
                        id='select-period',
                        min=0,
                        max=10,
                        step=None,
                        marks={
                            0: "year",
                            2.5: "9 months",
                            5: "6 months",
                            7.5: "3 months",
                            9: "month",
                            10: "week"
                        },
                        value=0
                    ),
                    dcc.Graph(id='graph-view')
                ]
            ),
            html.Div(
                id="tweets-view",
                className="list",
                children=[
                    html.Label("Analyzed tweets:")
                ]
            )
        ]
    )
])

@app.callback(
    Output("graph-view", "figure"),
    [Input("select-stock", "value"), Input('select-period', 'value')]
)
def show_stock_graph(ticker, period):
    # validate value
    if ticker is None:
        return {}

    # serach the period to show
    today = datetime.now()
    end_date = today.strftime('%Y-%m-%d')
    if period == 0:
        start_date = (today - relativedelta(years=1))
    elif period == 2.5:
        start_date = (today - relativedelta(months=9))
    elif period == 5:
        start_date = (today - relativedelta(months=6))
    elif period == 7.5:
        start_date = (today - relativedelta(months=3))
    elif period == 9:
        start_date = (today - relativedelta(months=1))
    elif period == 10:
        start_date = (today - relativedelta(weeks=1))
    start_date = start_date.strftime('%Y-%m-%d')

    # take the data from the correct file
    file_name = "data/historical_data/" + str(ticker) + ".json"
    target_stocks = pd.read_json(file_name, lines=True)
    target_stocks = target_stocks.set_index(['Date'])
    target_stocks = target_stocks.loc[start_date : end_date]
    fig = px.line(target_stocks,
                  x=target_stocks.index,
                  y="Close",
                  title=ticker,
                  render_mode="svg")
    return fig


@app.callback(
    Output('tweets-view', 'children'),
    Input("select-stock", "value")
)
def show_tweets(ticker):
    # validate the ticker selected
    if ticker is None:
        return
    # search new tweets
    get_tweets('update')
    fname = 'data/tweets/tweets_' + ticker + '.json'
    with open(fname, mode='r') as file:
        raw_tweets = pd.read_json(path_or_buf=file, orient='records', lines=True)
    raw_tweets = raw_tweets.set_index(['Date'])
    today = datetime.now()
    start_date = datetime(year=today.year, month=today.month, day=today.day, hour=0, minute=0, second=0).timestamp()
    end_date = datetime(year=today.year, month=today.month, day=today.day,
                        hour=today.hour, minute=today.minute, second=today.second).timestamp()
    new_tweets = raw_tweets.loc[start_date : end_date]
    print(new_tweets)
    # for line in new_tweets:
    #     tweet = json.loads(line)
    #     div = html.Div(
    #         children=[
    #             html.Cite("@" + tweet["Account_Name"]),
    #             html.P(tweet["Text"])
    #         ],
    #         style={"border-bottom": "solid grey 2px"}
    #     )
    # target_tweets.append(div)
    # clf = joblib.load('model/sentiment_classifier.pkl')
    # print('model downloaded\n')
    # tweet['Text'] = tweet['Text'].lower()
    # print('model downloaded\n')
    # tweet = select_only_english(tweet)
    # print('model downloaded\n')
    # tweet['Text'] = tweet['Text'].apply(remove_special_char)
    # print('filtering...')
    # mylist = [tweet["Text"]]
    # arr = np.asarray(mylist)
    # arr.reshape(-1, 1)
    # predicted = clf.predict(arr)
    # print("\n\n" + tweet['Text'] + "\n" + predicted)




    # Predicting


    # filter_tweets(target_file)
    # add the weigth
#
    # target_stocks = pd.read_json(("data/tweet" + ticker + ".json"), lines=True)
    # print(target_stocks.head())
    return target_tweets

if __name__ == '__main__':
    app.run_server(debug=True)

