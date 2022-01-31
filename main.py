
import dash
import pytz
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from plotly.subplots import make_subplots
from datetime import datetime
from dateutil.relativedelta import relativedelta

import common.costants as const
from classification.stock_prediction import predict_stock_trend
from classification.tweets_classification import classify_tweets, get_daily_polarity
from collecting.financial_news_collector import get_finhub_news
from collecting.mongo_manager import MongoManager
from collecting.stocks_collector import get_live_data
from preprocessing.tweet_cleaner import filter_tweets
from preprocessing.tweet_weight import set_tweets_weight

stylesheet = ['./assets/style.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = 'Stock Sentiment'

market_status = 'Open'

app.layout = html.Div([
    dcc.Store(id='data-stocks'),
    html.Div(
        id='container',
        children=[
            html.Div(
                className='app-header',
                children=[
                    html.Div('Stock Sentiment', className='title'),
                    html.Label('The best friend for your investments')
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
                            0: 'year',
                            1: '11 mth',
                            2: '10 mth',
                            3: '9 mth',
                            4: '8 mth',
                            5: '7 mth',
                            6: '6 mth',
                            7: '5 mth',
                            8: '4 mth',
                            9: '3 mth',
                            10: '2 mth',
                            11: '1 mth',
                            12: 'week',
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
                    dcc.Loading(
                        children=[
                            html.Div(
                                id='load-tweets',
                                className='list',
                                children=[]
                            )
                        ],
                        type='default'
                    )

                ]
            ),
            html.Hr(),
            html.Div(
                id='news-view',
                children=[
                    html.H4('Last Financial News', className='title'),
                    dcc.Loading(
                        children=[
                            html.Div(
                                id='load-news',
                                className='list',
                                children=[]
                            )
                        ],
                        type='default'
                    )
                ]
            )
        ]
    )
])


@app.callback(
    Output('market-index', 'children'),
    [Input('select-stock', 'value'), Input('update-time', 'n_intervals')]
)
def update_market_index(ticker, n):
    if ticker is not None:
        if n % 5 == 0:
            actual_close, change, pct_change = get_live_data(ticker)
            return [
                html.P('Actual close: ' + str(round(actual_close, 2))),
                html.P(
                    str(round(change, 2)) + '(' + str(round(pct_change - 100, 2)) + '%)',
                    style={'color': 'red' if change < 0 else 'green'}
                ),
            ]
        else:
            raise PreventUpdate
    else:
        return []


@app.callback(
    Output('market-view', 'children'),
    Input('update-time', 'n_intervals')
)
def update_market(n):
    today = datetime.utcnow() - relativedelta(hours=5)
    if (today.hour < 9) or (today.hour == 9 and today.minute < 30) or (today.hour >= 16):
        global market_status
        market_status = 'Closed'
    else:
        market_status = 'Open'
    return [
        html.Label('Market ' + market_status, style={'font-size': '28px', 'margin-right': '5px'}),
        html.Span(today.strftime('%Y-%m-%d'), style={'font-size': '26px', 'text-align': 'right'}),
        html.Span(today.strftime('%H:%M:%S'), style={'font-size': '22px', 'opacity': '0.8'}),
    ]


@app.callback(
    Output('graph-view', 'figure'),
    [Input('select-stock', 'value'), Input('select-period', 'value')]
)
def show_stock_graph(ticker, period):
    # validate value
    if ticker is None:
        return {}

    mongo_db = MongoManager()
    last_stocks = mongo_db.get_stocks(ticker, datetime.utcnow() - relativedelta(years=1), datetime.utcnow())

    all_stocks = last_stocks
    start_date = set_date(period[0])
    end_date = set_date(period[1])
    if start_date.date() == end_date.date():
        start_date = (start_date - relativedelta(weeks=1))

    date_range = (all_stocks['Date'] > start_date) & (all_stocks['Date'] <= end_date)
    all_stocks = all_stocks.loc[date_range]
    all_stocks.sort_values(['Date'], inplace=True)

    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(
        go.Scatter(
            x=all_stocks['Date'],
            y=all_stocks['Close'],
            name='Close'
        ),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(
            x=all_stocks['Date'],
            y=all_stocks['Polarity'],
            name='Polarity Score'
        ),
        secondary_y=True,
    )
    fig.update_layout(title_text=ticker)
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
    Input('select-stock', 'value')
)
def show_tweets(ticker):
    # validate the ticker selected
    if ticker is not None:
        # search new tweets
        mongo_db = MongoManager()
        today = datetime.utcnow()
        if market_status == 'Close' and today.hour > 21:
            start_date = datetime(today.year, today.month, today.day, 21, 0, 0, tzinfo=pytz.utc)
        else:
            start_date = datetime(today.year, today.month, today.day-1, 21, 0, 0, tzinfo=pytz.utc)
        # collecting
        raw_tweets = mongo_db.get_tweets(ticker, start_date, datetime.utcnow())
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
                    html.Cite('@' + tweet['Account_Name']),
                    html.P(tweet['Real_Text']),
                    html.Cite(tweet['Datetime'] - relativedelta(hours=4))
                ],
            )
            children.append(div)
        polarity_score = get_daily_polarity(processed_tweets)
        # synch with load_stocks
        last_stocks = mongo_db.get_stocks(ticker, datetime.utcnow() - relativedelta(years=1), datetime.utcnow())
        stocks_prediction = predict_stock_trend(last_stocks, polarity_score)
        prediction = [
            html.Cite('Polarity Score: '),
            html.P(str(int(polarity_score))),
            html.Cite('Trend Prediction:'),
            html.Img(
                src='assets/image/Up.png' if stocks_prediction == 1 else 'assets/image/Down.png',
                style={'width': '50px'}
            )
        ]
        return [children, prediction]
    else:
        return [[], []]


@app.callback(
    Output('load-news', 'children'),
    Input('select-stock', 'value')
)
def show_news(ticker):
    if ticker is not None:
        today = datetime.utcnow()
        start_date = (today - relativedelta(days=3)).strftime('%Y-%m-%d')
        end_date = (today + relativedelta(days=1)).strftime('%Y-%m-%d')
        news_df = get_finhub_news(ticker, start_date, end_date)
        children = []
        for index, row in news_df.iterrows():
            div = html.Div(
                className='news',
                children=[
                    html.Cite(row['Source']),
                    html.A(
                        children=html.H4(row['Headline']),
                        href=row['Url']
                    ),
                    html.P(row['Summary']),
                    html.Cite(datetime.fromtimestamp(row['Date']).strftime('%Y-%m-%d'))
                ]
            )
            children.append(div)
        return children


if __name__ == '__main__':
    app.run_server(debug=False)

