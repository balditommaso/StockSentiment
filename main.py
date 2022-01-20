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
from preprocessing.textCleaner import filter_tweets, select_only_keyword, select_only_english, remove_special_char
from collecting.stocks_collector import update_stocks
from collecting.tweet_collector import get_tweets

stylesheet = ['./assets/style.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

app.layout = html.Div([
    # update stocks data if needed
    update_stocks('update'),
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

    # company parameter
    for company in const.target_company:
        if company['ticker'] == ticker:
            keyword = company['name']
    keyword = keyword + " " + ticker

    # select the period
    start_date = (datetime.now() - relativedelta(hours=24)).strftime('%s')
    end_date = datetime.now().strftime('%s')

    target_file = get_tweets(start_date, end_date, keyword, ticker, "data")
    target_tweets = []
    with open(target_file, mode='r') as tweets_file:
        for line in tweets_file:
            tweet = json.loads(line)
            div = html.Div(
                children=[
                    html.Cite("@" + tweet["Account_Name"]),
                    html.P(tweet["Text"])
                ],
                style={"border-bottom": "solid grey 2px"}
            )
            target_tweets.append(div)
            clf = joblib.load('model/sentiment_classifier.pkl')
            print('model downloaded\n')
            tweet['Text'] = tweet['Text'].str.lower()
            print('model downloaded\n')
            tweet = select_only_english(tweet)
            print('model downloaded\n')
            tweet['Text'] = tweet['Text'].apply(remove_special_char)
            print('filtering...')
            mylist = [tweet["Text"]]
            arr = np.asarray(mylist)
            arr.reshape(-1, 1)
            predicted = clf.predict(arr)
            print("\n\n" + tweet['Text'] + "\n" + predicted)




    # Predicting


    # filter_tweets(target_file)
    # add the weigth
#
    # target_stocks = pd.read_json(("data/tweet" + ticker + ".json"), lines=True)
    # print(target_stocks.head())
    return target_tweets

if __name__ == '__main__':
    app.run_server(debug=True)

