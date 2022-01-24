import dash
import joblib
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pymongo import MongoClient

import common.costants as const
from classification.tweets_classification import classify_tweets, get_polarity_average
from collecting.financial_news_collector import get_finhub_news
from collecting.stocks_collector import get_live_data
from collecting.tweet_collector import update_tweets
from preprocessing.tweet_cleaner import filter_tweets
from preprocessing.tweet_weight import set_tweets_weight

stylesheet = ['./assets/style.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

market_status = 'Open'

actual_close = 0
change = 0
pct_change = 0


# start-up functions
#App.do_update()     # accidenti ai server di edo
update_tweets('init')

app.layout = html.Div([
    # create a loading page

    html.Div(
        id="container",
        children=[
            html.Div(
                className="app-header",
                children=[
                    html.Div('Stock Sentiment', className="title"),
                    html.Label("The best friend for your investments")
                ]
            ),
            dcc.Interval(
                id='update-time',
                interval=1000,
                n_intervals=0
            ),
            html.Div(
                id='market-view',
                children=[]
            ),
            html.Hr(),
            dcc.Dropdown(
                id='select-stock',
                placeholder='Select Stock',
                options=[{'label': i['name'], 'value': i['ticker']} for i in const.target_company],
                value=None
            ),
            html.Div(
                id='market-index',
                children=[],
            ),
            html.Div(
                id='prediction',
                children=[]
            ),
            html.Div(
                id='stocks-view',
                children=[
                    dcc.RangeSlider(
                        id='select-period',
                        min=0,
                        max=12,
                        step=None,
                        marks={
                            0: "year",
                            1: "11 months",
                            2: "10 months",
                            3: "9 months",
                            4: "8 months",
                            5: "7 months",
                            6: "6 months",
                            7: "5 months",
                            8: "4 months",
                            9: "3 months",
                            10: "2 months",
                            11: "1 month",
                            12: "today",
                        },
                        value=[0, 12],
                        allowCross=False
                    ),
                    dcc.Graph(id='graph-view')
                ]
            ),
            html.Div(
                id='tweets-view',
                children=[
                    html.Img(
                        src='assets/image/twitter_logo.png',
                        style={
                            'width': '70px',
                            'margin': '10px'
                        }
                    ),
                    html.Div(
                        id="load-tweets",
                        className="list",
                        children=[
                            html.Cite("Select one company")
                        ]
                    )
                ]
            ),
            html.Hr(),
            html.Div(
                id='news-view',
                children=[
                    html.H4('Last Financial News', className="title"),
                    html.Div(
                        id='load-news',
                        className='list',
                        children=[
                            html.Cite("Select one company")
                        ]
                    )
                ]
            )
        ]
    )
])

@app.callback(
    Output('market-index', 'children'),
    [Input("select-stock", "value"), Input('update-time', 'n_intervals')]
)
def update_market_index(ticker, n):
    if ticker is not None:
        if n % 5 == 0:
            global change
            global actual_close
            global pct_change
            actual_close, change, pct_change = get_live_data(ticker)
        return [
            html.P("Actual close: " + str(round(actual_close, 2))),
            html.P(
                str(round(change, 2)) + "(" + str(round(pct_change - 100, 2)) + "%)",
                style={'color': 'red' if change < 0 else 'green'}
            ),
        ]
    else:
        return []


@app.callback(
    Output('market-view', 'children'),
    Input('update-time', 'n_intervals')
)
def update_market(n):
    today = datetime.utcnow()
    if (today.hour <= 9 and today.minute < 30) or (today.hour > 16):
        global market_status
        market_status = 'Close'
    else:
        market_status = 'Open'
    return [
        html.Label("Market " + market_status, style={'font-size': '28px', 'margin-right': '5px'}),
        html.Span(today.strftime('%Y-%m-%d'), style={'font-size': '26px', 'text-align': 'right'}),
        html.Span(today.strftime('%H:%M:%S'), style={'font-size': '22px', 'opacity': '0.8'}),
    ]


@app.callback(
    Output("graph-view", "figure"),
    [Input("select-stock", "value"), Input('select-period', 'value')]
)
def show_stock_graph(ticker, period):
    # validate value
    if ticker is None:
        return {}

    start_date = set_date(period[0])
    end_date = set_date(period[1])
    if start_date.date() == end_date.date():
        start_date = (start_date - relativedelta(weeks=1))
    target_stocks = get_stocks(ticker, start_date, end_date)
    fig = make_subplots(subplot_titles=ticker, specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=target_stocks["Date"],
            y=target_stocks["Close"],
            name="Close"
        ),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(
            x=target_stocks["Date"],
            y=target_stocks["Polarity"],
            name="Polarity Score"
        ),
        secondary_y=True,
    )
    return fig


def set_date(period):
    today = datetime.utcnow()
    if period == 12:
        target_date = today
    elif period == 0:
        target_date = (today - relativedelta(years=1))
    else:
        target_date = (today - relativedelta(months=(12-period)))
    return target_date


@app.callback(
    [Output('load-tweets', 'children'), Output('prediction', 'children')],
    Input("select-stock", "value")
)
def show_tweets(ticker):
    # validate the ticker selected
    if ticker is not None:
        # search new tweets
        update_tweets(ticker)
        fname = 'data/tweets/tweets_' + ticker + '.json'
        with open(fname, mode='r') as file:
            raw_tweets = pd.read_json(path_or_buf=file, orient='records', lines=True)

        # pre-processing
        clean_tweets = filter_tweets(raw_tweets, ticker)
        weighted_tweets = set_tweets_weight(clean_tweets)
        # elaborate polarity
        processed_tweets = classify_tweets(weighted_tweets)

        children = []
        for index, tweet in processed_tweets.iterrows():
            div = html.Div(
                className=tweet['Polarity'],
                style={
                    'padding': '5px',
                    'border-top': 'solid lightgray 2px'
                },
                children=[
                    html.Cite("@" + tweet["Account_Name"]),
                    html.P(tweet['Real_Text'])
                ],
            )
            children.append(div)
        avg_polarity = get_polarity_average(processed_tweets)
        # TO DO: second classification model
        prediction = [html.P("Prediction:\n" + str(round(avg_polarity, 2)))]
        return [children, prediction]
    else:
        return [[],[]]


#@app.callback(
#     Output('', 'children'),
#     Input("select-stock", "value")
#)
#def show_news(ticker):
#    today = datetime.now().strftime('%Y-%m-%d')
#    news_df = get_finhub_news(ticker, today, today)
#    return news_df


def get_stocks(ticker, start_date, end_date):
    client = MongoClient('mongodb+srv://root:root@cluster0.wvzn3.mongodb.net/'
                         'Stock-Sentiment?retryWrites=true&w=majority')
    db = client['Stock-Sentiment']
    collection = db['Stocks']
    print(type(start_date))
    cursor = collection.find(
        {
            "Ticker": ticker,
            "Date": {"$gte": start_date, "$lte": end_date}
        },
        {
            "Date": 1,
            "Close": 1,
            "Ticker": 1,
            "Polarity": 1
        }
    )
    list_cur = list(cursor)
    print(pd.DataFrame(list_cur))
    return pd.DataFrame(list_cur)


if __name__ == '__main__':
    app.run_server(debug=True)

