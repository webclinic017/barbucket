"""
Todo:
- y-axis scaling with range slider
- 2 charts, long- and mid-term
- charts go on right hand side, next to table
- dark colorscheme
- possibility to integrate custom indicartors and oscillators
- visualize trading signals
"""

import pandas as pd
import json
import logging

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import dash_dangerously_set_inner_html

import plotly.offline as py
import plotly.graph_objs as go

from highcharts import Highchart


def build_datatable():

    # Setup logging
    logging.basicConfig(
        filename = 'show-results.log',
        level = logging.DEBUG,
        format = '%(asctime)s\t\t%(levelname)s\t\t%(message)s',
        datefmt = '%m-/%d-/%Y_%I:%M:%S.%p')

    # logging.debug('This message should go to the log file')
    # logging.info('So should this')
    # logging.warning('And this, too')
    # logging.error('And this, too')
    # logging.critical('And this, too')


    # Read all symbols from symbol list
    symbols = []
    file = open('xetra_etf_symbols.txt','r') 
    for line in file:
        symbols.append(line.rstrip())
    file.close()


    # Build table structure
    table_data = pd.DataFrame({'Symbol': [], 
                                'Full Name': [],
                                'Bad Data': []
                                })


    # Generate table data
    for symbol in symbols:

        # Get price data for symbols
        price_data = pd.read_csv(f'data\{symbol}.csv')
            

        # Add to "Symbol" column
        table_data.Symbol.append(symbol)


        # Add to "Full Name" column from json file
        logging.debug(f'Opening file for: {symbol}')
        file = open(f'data\{symbol}.json', 'r')
        logging.debug(f'Reading file for: {symbol}')
        data = json.load(file)
        if 'longName' in data.keys():
            name = data['longName']
        elif 'shortName' in data.keys():
            name = data['shortName']    
        else:
            name = 'No name provided.'
        table_data.Name.append(name)
        file.close()


        # Add to "Bad Data" column
        # TODO



    # Pre-filter table data
    # TODO
    table_data = table_data[table_data['Bad Data'] == False & 
                            table_data['second_column_name'] >= 0
                            ]


    # Return table data
    return table_data


# Build Dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dash_table.DataTable(
        id='datatable',
        columns=[
            {"name": column, "id": column, "deletable": False} 
            for column in df.columns.tolist()
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
    dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
        id='dangerous_html')
])


# Another line of the table was selected -> update graph
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
        return{'data': None}
    else:
        dff = pd.DataFrame(table_data)
        symbol = dff['Symbol'][active_row]
        filepath = f'data\\{symbol}.csv'
        quotes = pd.read_csv(filepath)
        quotes = quotes.iloc[-750:]

        chart = Highchart()
        chart.set_options('chart', {'inverted': True})

        options = {
            'title': {
                'text': 'Atmosphere Temperature by Altitude'
            },
            'subtitle': {
                'text': 'According to the Standard Atmosphere Model'
            },
            'xAxis': {
                'reversed': False,
                'title': {
                    'enabled': True,
                    'text': 'Altitude'
                },
                'labels': {
                    'formatter': 'function () {\
                        return this.value + "km";\
                    }'
                },
                'maxPadding': 0.05,
                'showLastLabel': True
            },
            'yAxis': {
                'title': {
                    'text': 'Temperature'
                },
                'labels': {
                    'formatter': "function () {\
                        return this.value + '°';\
                    }"
                },
                'lineWidth': 2
            },
            'legend': {
                'enabled': False
            },
            'tooltip': {
                'headerFormat': '<b>{series.name}</b><br/>',
                'pointFormat': '{point.x} km: {point.y}°C'
            }
        }

        chart.set_dict_options(options)
        data =  [[0, 15], [10, -50], [20, -56.5], [30, -46.5], [40, -22.1], 
        [50, -2.5], [60, -27.7], [70, -55.7], [80, -76.5]]
        chart.add_data_set(data, 'spline', 'Temperature', marker={'enabled': False}) 

        # return HTML content
        return str(chart)


        # trace = go.Ohlc(
        #         x=pd.to_datetime(quotes['Date'], format='%Y-%m-%d'),
        #         open=quotes['Open'],
        #         high=quotes['High'],
        #         low=quotes['Low'],
        #         close=quotes['Close'])
    
        # return{
        #     'data': [trace],
        #     'layout': go.Layout(
        #         xaxis={
        #             'title': 'xtitle',
        #             'type': 'date'
        #         },
        #         yaxis={
        #             'title': 'ytitle',
        #             'type': 'log',
        #             # 'autorange': True,
        #             'fixedrange': True,
        #             'side': 'right'
        #         },
        #         height=600,
        #         margin={'l': 10, 'b': 40, 't': 10, 'r': 40},
        #         legend={'x': 0, 'y': 1},
        #         hovermode='closest'
        #     ),
        #     'config': {
        #         'scrollZoom': True
        #     }
        # }


# Run Dash app
if __name__ == '__main__':
    app.run_server(debug=False)


datatable = build_datatable()
