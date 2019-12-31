# Imports
import ib_insync
import pandas as pd
import numpy as np
from datetime import datetime
import os

import data_management.contracts_db as contracts_db
import data_management.quotes_db as quotes_db


class TwsConnector():
    
    def __init__(self):
        self.abort_operation = False


    def on_error(self, reqId, errorCode, errorString, contract):
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

        # Abort receiving if systematical problem is detected
        non_critical_codes = [162, 200, 354, 2104, 2106, 2158]
        if errorCode not in non_critical_codes:
            print('Systemic problem detected. ' + str(errorCode) + ' - ' + errorString)
            self.abort_operation = True

        # Write error info to contract database, if error is related to contract
        if contract is not None:
            status_code = errorCode
            status_text = 'Error:' + str(errorCode) + '_' + str(errorString)
            conn = contracts_db.ContractsDB()
            conn.update_contract_status(
                symbol=contract.symbol,
                exchange=contract.exchange,
                currency=contract.currency,
                status_code=status_code,
                status_text=status_text)
            print(contract.symbol + '_' + contract.exchange + ' ' + status_text)


    def get_historical_data(self):
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
        ib.errorEvent += self.on_error
        ib.connect('127.0.0.1', 7497, clientId=1, readonly=True)

        # Get contracts data
        start_id = 0
        end_id = 1
        cont_db = contracts_db.ContractsDB()
        quot_db = quotes_db.QuotesDB()
        contracts = cont_db.get_contracts()

        # Iterate over contracts
        for current_contract in contracts[start_id:end_id]:

            # Abort requesting data
            if self.abort_operation is True:
                print('Aborting receiving.')
                break

            debug_string = current_contract['symbol'] + '_' + current_contract['exchange']
            print(debug_string, end='')

            # Calculate length of requested data
            if current_contract['status_code'] == 1:
                start_date = (current_contract['status_text'].split(':'))[1]
                end_date = datetime.today().strftime('%Y-%m-%d')
                ndays = np.busday_count(start_date, end_date)
                if ndays <= 4:
                    print(' Existing data is only ' + str(ndays) + ' days old. Contract aborted.')
                    print('-------------------------')
                    continue
                ndays += 4
                duration_str = str(ndays) + ' D'
            else:
                duration_str = "10 Y"
            
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

            # Reformatting of received bars
            quotes = []
            for bar in bars:
                quote = (current_contract['contract_id'],
                        bar.date.strftime('%Y-%m-%d'),
                        bar.open,
                        bar.high,
                        bar.low,
                        bar.close,
                        bar.volume)
                quotes.append(quote)

            # Inserting into database
            quot_db.insert_quotes(
                contract_id=current_contract['contract_id'], 
                quotes=quotes)

            # write finished info to contracts database
                # Todo: use last day of data instead of today
            timestamp_now = datetime.now()
            string_now = timestamp_now.strftime('%Y-%m-%d')

            status_code = 1
            status_text = 'data_ends:'+string_now
            cont_db.update_contract_status(
                symbol=current_contract['symbol'],
                exchange=current_contract['exchange'],
                currency=current_contract['currency'],
                status_code=status_code,
                status_text=status_text
            )

            print(' Data stored.')
            print('-------------------------')

        # Finishd all contracts
        print('******** All done. ********')
        ib.disconnect()
        # Todo: Try/catch disconnect


