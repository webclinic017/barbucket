# Imports
import ib_insync
import pandas as pd
import numpy as np
from datetime import datetime
import os
import data_management.contracts



def on_error(reqId, errorCode, errorString, contract):
    """
    Is called on errors and writes error details to contracts db.

    Args:
        reqId: Description.
        errorCode: Description.
        errorString: Description.
        contract: Description.

    Returns:
        Nothing

    Raises:
        No errors
    """

    if contract is not None:
        # write msg info to contracts database
        status = errorCode
        status_text = 'Error:' + str(errorCode) + '_' + str(errorString)
        conn = data_management.contracts.ContractsDB()
        conn.update_contract_status(
            symbol=contract.symbol,
            exchange=contract.exchange,
            status=status,
            status_text=status_text)
        print(contract.symbol + '_' + contract.exchange + ' ' + status_text)


def get_historical_data():
    """
    Description

    Args:
        None

    Returns:
        Nothing

    Raises:
        No errors
    """

    # Create connection object
    ib = ib_insync.ib.IB()
    ib.errorEvent += on_error
    ib.connect('127.0.0.1', 7497, clientId=1, readonly=True)

    # Get contracts data
    start_id = 4875
    end_id = 5000
    conn = data_management.contracts.ContractsDB()
    contracts = conn.get_contracts()

    # Iterate over contracts
    for current_contract in contracts[start_id:end_id]:
            # Todo: Make the loop stoppable
            # Todo: Add timeout

        contract_status = current_contract['status']
        contract_status_text = current_contract['status_text']

        debug_string = current_contract['symbol'] + '_' + current_contract['exchange']
        print(debug_string, end='')

        # Skip contract, if has error status
        # if contract_status.startswith('Error:'):
        #     print(' Contract data not available. ')
        #     print('-------------------------')
        #     continue

        # Calculate length of requested data
            # Todo: Skip contract on certain error status, eg. tws does not know this contract
            # todo: exit on certain error status, eg no connection
        if contract_status == 1:
            start_date = (contract_status_text.split(':'))[1]
            end_date = datetime.today().strftime('%Y-%m-%d')
            ndays = np.busday_count(start_date, end_date)
            if ndays <= 1:
                print(' Existing data is only ' + str(ndays) + ' days old. Contract aborted.')
                print('-------------------------')
                continue
            ndays += 4
            duration_str = str(ndays) + ' D'
        else:
            duration_str = "10 Y"
        
        if current_contract['symbol'] == 'XGSD' and current_contract['exchange'] == 'LSE':
            print(' Skipping XGSD_LSE.')
            print('-------------------------')
            continue
            # Todo: Fix me
        
        # Create contract and request data
        print(' Requsting data.', end='')
        ib_contract = ib_insync.contract.Stock(
            symbol=current_contract['symbol'],
            exchange=current_contract['exchange'],
            currency=current_contract['currency'])
        bars = ib.reqHistoricalData(
            ib_contract,
            endDateTime='',
            durationStr=duration_str,
            barSizeSetting='1 day',
            whatToShow='MIDPOINT',
            useRTH=True)
        
        if len(bars) == 0:
            print('No data received. Contract aborted.')
            print('-------------------------')
            continue

        print(' Receiving completed.', end='')

        df_new = ib_insync.util.df(bars)
        df_new = df_new[['date', 'open', 'high', 'low', 'close', 'volume']]
        df_new[['date']] = df_new[['date']].astype(str)
        df_new = df_new.set_index('date')

        # Append to existing file or create new file
        filename = (
            '/Users/martin/Google Drive/data/screener/' +
            current_contract['symbol'] +
            '_' +
            current_contract['exchange'] +
            '.csv')
        if contract_status_text.startswith('data_ends:'):
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

        status = 1
        status_text = 'data_ends:'+string_now
        conn = data_management.contracts.ContractsDB()
        conn.update_contract_status(
            symbol=current_contract['symbol'],
            exchange=current_contract['exchange'],
            status=status,
            status_text=status_text
        )

        print(' Data stored.')
        print('-------------------------')
        # ib.sleep(0.1)

    # Finish
    print('******** All done. ********')
    ib.disconnect()
    # Todo: Try/catch disconnect


