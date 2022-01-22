import dash
import joblib
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
import common.costants as const
from collecting.stocks_collector import update_stocks, get_live_data
from collecting.tweet_collector import update_tweets
from preprocessing.tweet_cleaner import filter_tweets
from preprocessing.tweet_weight import set_tweets_weight

stylesheet = ['./assets/style.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

market_status = 'Open'

# start-up functions
update_stocks('update')     # NOTE: should update only if it's the first time of the day
update_tweets('init')

app.layout = html.Div([
    # create a loading page

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
                children=[]
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
                        children=[]
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
    if ticker is None:
        return []
    today = datetime.today()
    actual_close, change, pct_change = get_live_data(ticker)
    return [
        html.P("Actual close: " + str(round(actual_close, 2))),
        html.P(
            str(round(change, 2)) + "(" + str(round(pct_change - 100, 2)) + "%)",
            style={'color': 'red' if change < 0 else 'green'}
        ),
    ]


@app.callback(
    Output('market-view', 'children'),
    Input('update-time', 'n_intervals')
)
def update_market(n):
    today = datetime.today()
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
    Output('load-tweets', 'children'),
    Input("select-stock", "value")
)
def show_tweets(ticker):
    # validate the ticker selected
    if ticker is None or ticker == 'SPY':
        return
    # search new tweets
    update_tweets(ticker)
    fname = 'data/tweets/tweets_' + ticker + '.json'
    with open(fname, mode='r') as file:
        raw_tweets = pd.read_json(path_or_buf=file, orient='records', lines=True)
    # pre-processing
    pd.options.display.max_columns = None
    clean_tweets = filter_tweets(raw_tweets, ticker)
    weighted_tweets = set_tweets_weight(clean_tweets)
    # elaborate polarity
    clf = joblib.load('model/sentiment_classifier.pkl')
    prediction = clf.predict(weighted_tweets["Text"].values)
    weighted_tweets['Polarity'] = prediction

    children = []
    for index, tweet in weighted_tweets.iterrows():
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
    return children


if __name__ == '__main__':
    app.run_server(debug=True)

