# Imports
import ib_insync
import pandas as pd
import numpy as np
from tinydb import TinyDB, Query
from datetime import datetime
import os
# from ibpythonic import ibConnection, message
# from ibapi.contract import Contract
# from time import sleep, strftime
# import pickle
# from multiprocessing import Pool
# import ib_data.workers
# from tqdm import tqdm


# End of historical data handler
def my_hist_data_end_handler(msg):

    # Merge collected data into dataframe
    df_new = pd.DataFrame(columns=('date', 'open', 'high', 'low', 'close', 'volume'))
    for bar in bar_data_list:
        dashed_date = bar.date[:4] + '-' + bar.date[4:6] + '-' + bar.date[6:]
        row = {'date': dashed_date, 'open': bar.open, 'high': bar.high, 'low': bar.low, 'close': bar.close, 'volume': bar.volume}
        df_new = df_new.append(row, ignore_index=True)
    # df_new.loc[:, 'date'] = pd.to_datetime(df_new.date, format='%Y%m%d') #'%Y%m%d  %H:%M:%S'
    df_new = df_new.set_index('date')

    # Check if there is already existing data
    contracts_db = TinyDB('contracts_db.json')
    my_query = Query()
    result = contracts_db.search(my_query.Id == active_contract_id)
    contracts_db.close()
    current_contract = result[0]        
    contract_status = current_contract['Status']
    contract_symbol = current_contract['Symbol']
    contract_exchange = current_contract['Exchange']

    # Append to existing file or create new file
    filename = '/Users/martin/Google Drive/data/screener/' + contract_symbol + '_' + contract_exchange + '.csv'
    if contract_status.startswith('data_ends:'):
        df_old = pd.read_csv(filename, index_col='date')
        df_combined = df_new.combine_first(df_old)
        os.remove(filename)
        df_combined.to_csv(filename)
    else:
        if os.path.exists(filename):
            os.remove(filename)
        df_new.to_csv(filename)

    # write finished info to contracts database
        # Todo: use last day of data instead of today
    timestamp_now = datetime.now()
    string_now = timestamp_now.strftime('%Y-%m-%d') 
    contracts_db = TinyDB('contracts_db.json')
    my_query = Query()
    contracts_db.update({'Status': 'data_ends:'+string_now}, my_query.Id == active_contract_id)
    contracts_db.close()

    print(contract_symbol + '_' + contract_exchange + ' successful.')

    bar_data_list = []
    active_contract_id = 0
    busy = False


# Error handler
def on_error(reqId, errorCode, errorString, contract):
    if contract is not None:
        # write msg info to contracts database
        contracts_db = TinyDB('ib_insync/contracts_db.json')
        my_query = Query()
        status = 'Error:' + str(errorCode) + '_' + str(errorString)
        status = status.replace("'", "")
        contracts_db.update(
            {'Status': status},
            (my_query.Sybol == contract.symbol and
            my_query.Exchange == contract.exchange))
            # Todo: Use ConId
        contracts_db.close()
        print(contract.symbol + '_' + contract.exchange + ' ' + status)


# Create connection object
ib = ib_insync.ib.IB()
ib.errorEvent += on_error
ib.connect('127.0.0.1', 7497, clientId=1, readonly=True)

start_id = 20
end_id = 40
for index in range(start_id, end_id):
        # Todo: Make the loop stoppable
        # Todo: Add timeout
    
    # Get contract data from contracts db
    contracts_db = TinyDB('ib_insync/contracts_db.json')
    my_query = Query()
    result = contracts_db.search(my_query.Id == index)
    contracts_db.close()
    current_contract = result[0]
    contract_status = current_contract['Status']
    debug_string = str(index) + ': ' + current_contract['Symbol'] + '_' + current_contract['Exchange'] + ' requesting. '
    print(debug_string, end='')
    
    # Calculate length of requested data
        # Todo: Skip contract on certain error status, eg. tws does not know this contract
        # todo: exit on certain error status, eg no connection
    if contract_status.startswith('data_ends:'):
        start_date = (contract_status.split(':'))[1]
        end_date = datetime.today().strftime('%Y-%m-%d')
        ndays = np.busday_count(start_date, end_date)
        if ndays <= 1:
            print('data is up to date. ' + str(ndays))
            continue
        ndays += 4
        duration_str = str(ndays) + ' D'
    else:
        duration_str = "10 Y"
    
    if current_contract['Symbol'] == 'XGSD' and current_contract['Exchange'] == 'LSE':
        print('Skipping XGSD_LSE.')
        continue
        # Todo: Fix me
    
    # Create contract and request data
    ib_contract = ib_insync.contract.Stock(
        symbol=current_contract['Symbol'],
        exchange=current_contract['Exchange'],
        currency=current_contract['Currency'])
    bars = ib.reqHistoricalData(
        ib_contract,
        endDateTime='',
        durationStr=duration_str,
        barSizeSetting='1 day',
        whatToShow='MIDPOINT',
        useRTH=True)
    
    if len(bars) == 0:
        print('no data. aborted.')
    else:
        print('completed.')

        df_new = ib_insync.util.df(bars)
        df_new = df_new[['date', 'open', 'high', 'low', 'close', 'volume']]
        df_new[['date']] = df_new[['date']].astype(str)
        df_new = df_new.set_index('date')

        # Append to existing file or create new file
        filename = (
            '/Users/martin/Google Drive/data/screener/' +
            current_contract['Symbol'] +
            '_' +
            current_contract['Exchange'] +
            '.csv')
        if contract_status.startswith('data_ends:'):
            df_old = pd.read_csv(filename, index_col='date')
            df_combined = df_new.combine_first(df_old)
            os.remove(filename)
            df_combined.to_csv(filename)
        else:
            if os.path.exists(filename):
                os.remove(filename)
            df_new.to_csv(filename)

        # write finished info to contracts database
            # Todo: use last day of data instead of today
        timestamp_now = datetime.now()
        string_now = timestamp_now.strftime('%Y-%m-%d') 
        contracts_db = TinyDB('ib_insync/contracts_db.json')
        my_query = Query()
        contracts_db.update({'Status': 'data_ends:'+string_now}, my_query.Id == index)
        contracts_db.close()

        print(current_contract['Symbol'] + '_' + current_contract['Exchange'] + ' successful.')
    print('-------------------------')
    ib.sleep(0.2)

print('******** All done. ********')
ib.disconnect()
# Todo: Try/catch disconnect


