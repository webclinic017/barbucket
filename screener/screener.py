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


def get_trading_days(start, end):
    '''
    start: 'YYYY-MM-DD'
    end: 'YYYY-MM-DD'
    '''

    quotes = pd.read_csv('data\\^GDAXI.csv')
    quotes = quotes.set_index('Date')
    quotes = quotes[start:end]

    return len(quotes.index)


def bad_data (
    df, 
    index_trading_days, 
    max_missing_bars = 0, 
    # max_missing_bars_at_end = 0, 
    # max_missing_bars_at_begin = 0, 
    max_invalid_candle = 0,
    max_value_jump = 25,
    max_no_movement = 5):
    '''
    df: 
    index_trading_days: int
    max_missing_bars = 0: 
    max_missing_bars_at_end = 0: 
    max_missing_bars_at_begin = 0: 
    max_invalid_candle = 0:
    max_value_jump = 25:
    max_no_movement = 5:
    '''

    result = {
        'flag': False,
        'missing_bars': 0,
        # 'missing_bars_at_begin': 0,
        # 'missing_bars_at_end': 0,
        'invalid_candle': [],
        'value_jump': [],
        'no_movement': []
    }


    # Missing bars overall
    result['missing_bars'] = index_trading_days - len(df)


    # Missing bars at begin
    # result.missing_bars_at_begin = df.index[0] - index_trading_days[0]

    # Missing bars at end
    # result.missing_bars_at_end = index_trading_days[-1] - df.index[-1]


    for index, candle in df.iterrows():

        # Invalid candle
        if max(candle.Open, candle.Low, candle.Close) > candle.High or min(
        candle.Open, candle.High, candle.Close) < candle.Low:
            result['invalid_candle'].append(True)
        else:
            result['invalid_candle'].append(False)

        # Value jumps
        # FIXME
        result['value_jump'].append(False)

        # No movement from this open to this close
        if candle.Close == candle.Open:
            result['no_movement'].append(True)
        else:
            result['no_movement'].append(False)

    
    # Calculate result flag
    if (
        result['missing_bars'] > max_missing_bars or
        # result['missing_bars_at_begin'] > max_missing_bars_at_begin or
        # result['missing_bars_at_end'] > max_missing_bars_at_end or
        result['invalid_candle'].count(True) > max_invalid_candle or
        result['value_jump'].count(True) > max_value_jump or
        result['no_movement'].count(True) > max_no_movement
    ):
        result['flag'] = False
    else:
        result['flag'] = True


    return result


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


    # Initialize empty dataframe
    table_data = pd.DataFrame()


    # Generate table data
    for symbol in symbols:

        row_data = {}

        # Get price data for symbols
        try:
            price_data = pd.read_csv(f'data\{symbol}.csv', index_col=0, parse_dates=True)
        except:
            continue
        
        price_data = price_data['2018-01-01':]    

        # Add to "Symbol" column
        row_data['Symbol'] = symbol


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
        row_data['Name'] = name
        file.close()


        # Add to "Bad Data" column
        bd_result = bad_data(price_data, 351, 4, 4, 4, 4)
        row_data['Missing bars'] = bd_result['missing_bars']


        table_data = table_data.append(row_data, ignore_index=True)



    # Pre-filter table data
    # TODO
    # table_data = table_data[table_data['Bad Data'] == False & 
    #                         table_data['second_column_name'] >= 0
    #                         ]


    # Return table data
    return table_data


# Build Dash app
df = build_datatable()

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
    dcc.Graph(id='chart')
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
        quotes = pd.read_csv(filepath, index_col=0, parse_dates=True)
        quotes = quotes['2018-01-01':]

        trace = go.Ohlc(
                # x=pd.to_datetime(quotes['Date'], format='%Y-%m-%d'),
                x=quotes.index,
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
                    'fixedrange': True,
                    'side': 'right'
                },
                height=600,
                margin={'l': 10, 'b': 40, 't': 10, 'r': 40},
                legend={'x': 0, 'y': 1},
                hovermode='closest'
            ),
            'config': {
                'scrollZoom': True
            }
        }


# Run Dash app
if __name__ == '__main__':
    app.run_server(debug=False)