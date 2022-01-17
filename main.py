import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

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
                    dcc.RangeSlider(
                        id='select-period',

                    ),
                    dcc.Graph(id='graph-view'),
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
    Input("select-stock", "value")
)
def show_stock_graph(ticker):
    print(ticker)
    if ticker is None:
        return {}
    file_name = "data/historical_data/" + str(ticker) + ".json"
    stocks_df = pd.read_json(file_name, lines=True)
    fig = px.line(stocks_df,
                  x="Date",
                  y="Open",
                  title=ticker,
                  line_shape="spline",
                  render_mode="svg")
    return fig

# load tweets of the day


if __name__ == '__main__':
    update_stocks()
    app.run_server(debug=True)

