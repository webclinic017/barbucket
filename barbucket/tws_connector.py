# Imports
import ib_insync
import pandas as pd
import numpy as np
from datetime import datetime
import os
import configparser

import barbucket.contracts_db as contracts_db
import barbucket.quotes_db as quotes_db
import barbucket.data_quality_check as data_quality_check


class TwsConnector():
    
    def __init__(self):
        self.__contracts_db = contracts_db.ContractsDB()
        self.__quotes_db = quotes_db.QuotesDB()
        self.__data_quality_check = data_quality_check.DataQualityCheck()
        
        self.__config = configparser.ConfigParser()
        self.__config.read('barbucket/config.ini')

        self.abort_operation = False


    def __on_error(self, reqId, errorCode, errorString, contract):
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
        NON_SYSTEMIC_CODES = self.__config.get('tws_connector',
            'non_systemic_codes').split(',')
        NON_SYSTEMIC_CODES = list(map(int, NON_SYSTEMIC_CODES))
        if errorCode not in NON_SYSTEMIC_CODES:
            print('Systemic problem detected. ' + str(errorCode) + ' - ' + 
                errorString)
            self.abort_operation = True

        # Write error info to contract database, if error is related to contract
        if contract is not None:
            status_code = errorCode
            status_text = 'Error:' + str(errorCode) + '_' + str(errorString)
            self.__contracts_db.update_contract_status(
                symbol=contract.symbol,
                exchange=contract.exchange,
                currency=contract.currency,
                status_code=status_code,
                status_text=status_text)
            print(contract.symbol + '_' + contract.exchange + ' ' + status_text)


    def get_historical_data(self):
        # Todo: on_eror -> on_tws_error
        # Todo: Outsourcing of abortions of the contract handling 
        #       (quality_check, db_handling)
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
        ib.errorEvent += self.__on_error

        IP = self.__config.get('tws_connector', 'ip')
        PORT = self.__config.getint('tws_connector', 'port')
        ib.connect(host=IP, port=PORT, clientId=1, readonly=True)

        # Get config constants
        REDOWNLOAD_DAYS = self.__config.getint('tws_connector', 'redownload_days')

        # Get contracts data
        contracts = self.__contracts_db.get_contracts()

        try:
            # Iterate over contracts
            for contract in contracts:

                # Abort requesting data
                if self.abort_operation is True:
                    print('Aborting operation.')
                    break

                debug_string = contract['symbol'] + '_' + contract['exchange']
                print(debug_string, end='')

                # Calculate length of requested data
                if contract['status_code'] == 1:
                    start_date = (contract['status_text'].split(':'))[1]
                    end_date = datetime.today().strftime('%Y-%m-%d')
                    ndays = np.busday_count(start_date, end_date)
                    if ndays <= REDOWNLOAD_DAYS:
                        print(' Existing data is only ' + str(ndays) + 
                            ' days old. Contract aborted.')
                        print('-------------------------')
                        continue
                    if ndays > 360:
                        print(' Last Download is ' + str(ndays) + 
                            ' days old. Contract aborted.')
                        print('-------------------------')
                        continue
                    ndays += 6
                    duration_str = str(ndays) + ' D'
                else:
                    duration_str = "10 Y"
                
                # Create contract and request data
                print(' Requsting data.', end='')
                ib_contract = ib_insync.contract.Stock(
                    symbol=contract['symbol'],
                    exchange=contract['exchange'],
                    currency=contract['currency'])
                bars = ib.reqHistoricalData(
                    ib_contract,
                    endDateTime='',
                    durationStr=duration_str,
                    barSizeSetting='1 day',
                    whatToShow='ADJUSTED_LAST',
                    useRTH=True)
                
                if len(bars) == 0:
                    print('No data received.', end='')
                    # Check data quality
                    self.__data_quality_check.handle_single_contract(
                        contract['contract_id'])
                    print(' Quality check done.')
                    print('-------------------------')
                    continue

                print(' Receiving completed.', end='')

                # Reformatting of received bars
                quotes = []
                for bar in bars:
                    quote = (contract['contract_id'],
                        bar.date.strftime('%Y-%m-%d'),
                        bar.open,
                        bar.high,
                        bar.low,
                        bar.close,
                        bar.volume)
                    quotes.append(quote)

                # Inserting into database
                self.__quotes_db.insert_quotes(quotes=quotes)

                # write finished info to contracts database
                status_code = 1
                timestamp_now = datetime.now()
                string_now = timestamp_now.strftime('%Y-%m-%d')
                status_text = 'downloaded:' + string_now
                self.__contracts_db.update_contract_status(
                    symbol=contract['symbol'],
                    exchange=contract['exchange'],
                    currency=contract['currency'],
                    status_code=status_code,
                    status_text=status_text
                )
                print(' Data stored.', end='')

                # Check data quality
                self.__data_quality_check.handle_single_contract(
                    contract['contract_id'])
                print(' Qualty check done.')
                print('-------------------------')

        except KeyboardInterrupt:
            print('Keyboard interrupt detected.', end='')
            self.abort_operation = True

        finally:
            ib.disconnect()
            print('Disconnected.')

        # Finishd all contracts
        print('******** All done. ********')



