import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

import common.costants as const
from collecting.stocks_collector import update_stocks

stylesheet = ['./assets/style.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

app.layout = html.Div([
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
                    html.Button(
                        "Predict",
                        id='predict'
                    )
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
        start_date = (today - relativedelta(years=1)).strftime('%Y-%m-%d')
    elif period == 2.5:
        start_date = (today - relativedelta(months=9)).strftime('%Y-%m-%d')
    elif period == 5:
        start_date = (today - relativedelta(months=6)).strftime('%Y-%m-%d')
    elif period == 7.5:
        start_date = (today - relativedelta(months=3)).strftime('%Y-%m-%d')
    elif period == 9:
        start_date = (today - relativedelta(months=1)).strftime('%Y-%m-%d')
    elif period == 10:
        start_date = (today - relativedelta(weeks=1)).strftime('%Y-%m-%d')
    print(end_date)
    file_name = "data/historical_data/" + str(ticker) + ".json"
    target_stocks = pd.read_json(file_name, lines=True)
    target_stocks = target_stocks.set_index(['Date'])
    target_stocks = target_stocks.loc[start_date : end_date]
    fig = px.line(target_stocks,
                  x=target_stocks.index,
                  y="Open",
                  title=ticker,
                  render_mode="svg")
    return fig

# load tweets of the day


if __name__ == '__main__':
    update_stocks()
    app.run_server(debug=True)

