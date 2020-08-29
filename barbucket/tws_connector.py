# Imports
import ib_insync
import pandas as pd
import numpy as np
from datetime import datetime
import os
import configparser

from barbucket.universes_db import UniversesDB
from barbucket.contracts_db import ContractsDB
from barbucket.contract_details_db import ContractDetailsDB
from barbucket.quotes_db import QuotesDB
from barbucket.data_quality_check import DataQualityCheck
from barbucket.config import get_config_value


class TwsConnector():
    
    def __init__(self):
        self.__universes_db = UniversesDB()
        self.__contracts_db = ContractsDB()
        self.__contract_details_db = ContractDetailsDB()
        self.__quotes_db = QuotesDB()
        self.__data_quality_check = DataQualityCheck()
        self.abort_operation = False


    def __on_get_histo_error(self, reqId, errorCode, errorString, contract):
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
        NON_SYSTEMIC_CODES = get_config_value('tws_connector',
            'non_systemic_codes')
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


    def get_historical_data(self, universe):
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
        ib.errorEvent += self.__on_get_histo_error

        IP = get_config_value('tws_connector', 'ip')
        PORT = int(get_config_value('tws_connector', 'port'))
        ib.connect(host=IP, port=PORT, clientId=1, readonly=True)

        # Get config constants
        REDOWNLOAD_DAYS = int(get_config_value('tws_connector',
            'redownload_days'))

        # Exchange codes
        exchange_codes = {
            "NASDAQ": "ISLAND",
            "NYSE": "NYSE",
            "ARCA": "ARCA",
            "AMEX": "AMEX",
            "FWB": "FWB",
            "IBIS": "IBIS",
            "LSE": "LSE",
            "LSEETF": "LSEETF"
        }
        # Get contracts for specified universe
        contracts = self.__universes_db.get_universe_members(universe)

        try:
            # Iterate over contracts
            for con_id in contracts:

                # Abort requesting data
                if self.abort_operation is True:
                    print('Aborting operation.')
                    break

                contract = self.__contracts_db.get_contracts(contract_id = con_id)[0]
                debug_string = contract['broker_symbol'] + '_' + contract['exchange']
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
                    duration_str = "15 Y"
                
                # Create contract and request data
                print(' Requsting data.', end='')
                ib_contract = ib_insync.contract.Stock(
                    symbol=contract['broker_symbol'],
                    exchange=exchange_codes[contract['exchange']],
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
                    # self.__data_quality_check.handle_single_contract(
                    #     contract['contract_id'])
                    # print(' Quality check done.')
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
                    symbol=contract['broker_symbol'],
                    exchange=contract['exchange'],
                    currency=contract['currency'],
                    status_code=status_code,
                    status_text=status_text
                )
                print(' Data stored.', end='')

                # Check data quality
                # self.__data_quality_check.handle_single_contract(
                #     contract['contract_id'])
                # print(' Qualty check done.')
                print('-------------------------')

        except KeyboardInterrupt:
            print('Keyboard interrupt detected.', end='')
            self.abort_operation = True

        finally:
            ib.disconnect()
            print('Disconnected.')

        # Finishd all contracts
        print('******** All done. ********')


    def __on_get_details_error(self, reqId, errorCode, errorString, contract):
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

        # # Abort receiving if systematical problem is detected
        # NON_SYSTEMIC_CODES = get_config_value('tws_connector',
        #     'non_systemic_codes')
        # NON_SYSTEMIC_CODES = list(map(int, NON_SYSTEMIC_CODES))
        # if errorCode not in NON_SYSTEMIC_CODES:
        #     print('Systemic problem detected. ' + str(errorCode) + ' - ' + 
        #         errorString)
        #     self.abort_operation = True

        # # Write error info to contract database, if error is related to contract
        # if contract is not None:
        #     status_code = errorCode
        #     status_text = 'Error:' + str(errorCode) + '_' + str(errorString)
        #     self.__contracts_db.update_contract_status(
        #         symbol=contract.symbol,
        #         exchange=contract.exchange,
        #         currency=contract.currency,
        #         status_code=status_code,
        #         status_text=status_text)
        #     print(contract.symbol + '_' + contract.exchange + ' ' + status_text)


    def get_contract_details(self):
        # Create connection object
        ib = ib_insync.ib.IB()
        ib.errorEvent += self.__on_get_details_error

        IP = get_config_value('tws_connector', 'ip')
        PORT = int(get_config_value('tws_connector', 'port'))
        ib.connect(host=IP, port=PORT, clientId=1, readonly=True)

        # Exchange codes
        exchange_codes = {
            "NASDAQ": "ISLAND",
            "ISLAND": "ISLAND",
            "NYSE": "NYSE",
            "ARCA": "ARCA",
            "AMEX": "AMEX",
            "FWB": "FWB",
            "IBIS": "IBIS",
            "LSE": "LSE",
            "LSEETF": "LSEETF"
        }

        # Get all contract_ids
        contracts = self.__contracts_db.get_contracts()

        try:
            # Iterate over contracts
            for contract in contracts:

                con_id = contract["contract_id"]

                # Abort requesting data
                if self.abort_operation is True:
                    print('Aborting operation.')
                    break

                debug_string = contract['broker_symbol'] + '_' + contract['exchange']
                print(debug_string, end='')
                
                # Abort contract, if details are already present in db
                details = self.__contract_details_db.get_ib_contract_details(
                    contract_id=con_id)
                if details != None:
                    print('Details already present in db.')
                    continue
                
                # Create contract-object and request data
                print(' Requsting data.', end='')
                ib_contract = ib_insync.contract.Stock(
                    symbol=contract['broker_symbol'],
                    exchange=exchange_codes[contract['exchange']],
                    currency=contract['currency'])

                details = ib.reqContractDetails(ib_contract)
                if len(details) > 0:
                    details = details[0]
                else:
                    print("No details returned.")
                    continue
                
                # if len(details) == 0:
                #     print('No data received.', end='')
                #     # Check data quality
                #     # self.__data_quality_check.handle_single_contract(
                #     #     contract['contract_id'])
                #     # print(' Quality check done.')
                #     print('-------------------------')
                #     continue

                print(' Receiving completed.', end='')

                ### Inserting into database
                self.__contract_details_db.insert_ib_contract_details(con_id,
                    details.industry, details.category, details.subcategory,
                    details.contract.conId, details.contract.primaryExchange,
                    details.stockType)

                print(' Data stored.', end='')

                ### Check data quality
                # print(' Qualty check done.')
                print('-------------------------')

        except KeyboardInterrupt:
            print('Keyboard interrupt detected.', end='')
            self.abort_operation = True

        finally:
            ib.disconnect()
            print('Disconnected.')

        # Finishd all contracts
        print('******** All done. ********')