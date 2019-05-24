import pandas as pd
import json
import logging


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


# Export table data to pickle file
table_data.to_pickle('table_data.pkl')

