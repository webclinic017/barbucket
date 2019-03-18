"""
Todo:
- y-axis scaling with range slider
- 2 charts, long- and mid-term
- charts go on right hand side, next to table
- dark colorscheme
- possibility to integrate custom indicartors and oscillators
- visualize trading signals
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State

import plotly.offline as py
import plotly.graph_objs as go

import pandas as pd

df = pd.DataFrame({'Symbol': ['AAPL', 'GOOG', 'MSFT', 'FB'],
                    'Growth': [20, 30, 40, 50],
                    'Channel width': [90, 80, 70, 60]})


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dash_table.DataTable(
        id='datatable',
        columns=[
            {"name": i, "id": i, "deletable": False} for i in df.columns
        ],
        data=df.to_dict("rows"),
        editable=False,
        filtering=True,
        sorting=True,
        sorting_type="multi",
        row_selectable=False,
        row_deletable=False,
        selected_rows=[],
        pagination_mode=False
    ),
    dcc.Graph(id='chart')
])


@app.callback(
    Output('chart', "figure"),
    [Input('datatable', "active_cell")],
    [State('datatable', "derived_viewport_data")]
)
def update_output(active_cell, table_data):
    if active_cell is None:
        active_row = 1
    else:
        active_row = active_cell[0]

    if table_data is None:
        return{
        'data': None
        }
    else:
        dff = pd.DataFrame(table_data)
        symbol = dff['Symbol'][active_row]
        filepath = f'C:\\Program Files\\AmiBroker\\AmiQuote\\Download\\{symbol}.aqh'
        quotes = pd.read_csv(filepath, skiprows=1)
        quotes = quotes.iloc[-750:]

        trace = go.Ohlc(
                x=pd.to_datetime(quotes['# Date'], format='%d-%m-%Y'),
                open=quotes['Open'],
                high=quotes['High'],
                low=quotes['Low'],
                close=quotes['Close'])
    
        return{
            'data': [trace],
            'layout': go.Layout(
                xaxis={
                    'title': 'xtitle',
                    'type': 'date'
                },
                yaxis={
                    'title': 'ytitle',
                    'type': 'log',
                    'autorange': True,
                    'fixedrange': False
                },
                height=800,
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }

if __name__ == '__main__':
    app.run_server(debug=False)