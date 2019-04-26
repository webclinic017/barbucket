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
import json

symbols = []
file = open('xetra_etf_symbols.txt','r') 
for line in file:
    symbols.append(line.rstrip())
file.close()

names = []
for symbol in symbols:
    file = open(f'data\{symbol}.json', 'r')
    data = json.load(file)
    if 'longName' in data.keys():
        name = data['longName']
    elif 'shortName' in data.keys():
        name = data['shortName']    
    else:
        name = 'No name provided.'
    names.append(name)

df = pd.DataFrame({'Symbol': symbols,
    'Name': names})

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dash_table.DataTable(
        id='datatable',
        columns=[
            {"name": i, "id": i, "deletable": False} for i in df.columns.tolist()
        ],
        style_cell={'textAlign': 'left'},
        style_cell_conditional=[
            {
                'if': {'column_id': 'Region'},
                'textAlign': 'left'
            }
        ],
        data=df.to_dict("rows"),
        editable=False,
        filtering=True,
        sorting=True,
        sorting_type="multi",
        row_selectable=False,
        row_deletable=False,
        selected_rows=[],
        pagination_mode=False,
        style_table={
            'maxHeight': '300',
            'overflowY': 'scroll'
        }
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
        # filepath = f'C:\\Program Files\\AmiBroker\\AmiQuote\\Download\\{symbol}.aqh'
        filepath = f'data\\{symbol}.csv'
        quotes = pd.read_csv(filepath)
        quotes = quotes.iloc[-750:]

        trace = go.Ohlc(
                x=pd.to_datetime(quotes['Date'], format='%Y-%m-%d'),
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
                height=600,
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            )
        }

if __name__ == '__main__':
    app.run_server(debug=False)