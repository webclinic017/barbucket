# Imports
import ib_insync
import pandas as pd
import numpy as np
from datetime import datetime
import os
import configparser

# from barbucket.universes_db import UniversesDB
# from barbucket.contracts_db import ContractsDB
# from barbucket.contract_details_db import ContractDetailsDB
# from barbucket.quotes_db import QuotesDB
# from barbucket.data_quality_check import DataQualityCheck
from barbucket.config import get_config_value


class TwsConnector():
    
    def __init__(self):
        # Create connection object
        self.__ib = ib_insync.ib.IB()
        # Register own error handler on ib hook
        self.__ib.errorEvent += self.__on_tws_error
        self.__connection_error = False



    def __encode_exchange(self, exchange):
        exchange_codes = {
            'NASDAQ': "ISLAND",     # NASDAQ / Island
            'ISLAND': "ISLAND",     # NASDAQ / Island
            'NYSE': "NYSE",         # NYSE
            'ARCA': "ARCA",         # Archipelago
            'AMEX': "AMEX",         # American Stock Exchange
            'BATS': "BATS",         # Better Alternative Trading System

            'VSE': "VSE",           # Vancouver Stock Exchange

            'FWB': "FWB",           # Frankfurter Wertpapierbörse
            'IBIS': "IBIS",         # XETRA
            'SWB': "SWB",           # Stuttgarter Wertpapierbörse

            'LSE': "LSE",           # London Stock Exchange
            'LSEETF': "LSEETF",     # London Stock Exchange: ETF

            'SBF': "SBF"}           # Euronext France

        return exchange_codes[exchange]



    def __decode_exchange(self, exchange):
        exchange_codes = {
            'ISLAND': "NASDAQ",     # NASDAQ / Island
            'NASDAQ': "NASDAQ",     # NASDAQ / Island
            'NYSE': "NYSE",         # NYSE
            'ARCA': "ARCA",         # Archipelago
            'AMEX': "AMEX",         # American Stock Exchange
            'BATS': "BATS",         # Better Alternative Trading System

            'VSE': "VSE",           # Vancouver Stock Exchange

            'FWB': "FWB",           # Frankfurter Wertpapierbörse
            'IBIS': "IBIS",         # XETRA
            'SWB': "SWB",           # Stuttgarter Wertpapierbörse

            'LSE': "LSE",           # London Stock Exchange
            'LSEETF': "LSEETF",     # London Stock Exchange: ETF

            'SBF': "SBF"}           # Euronext France

        return exchange_codes[exchange]



    def __on_tws_error(self, reqId, errorCode, errorString, contract):
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
            self.__connection_error = True

        # Write error info to contract database, if error is related to contract
        # Todo: Better check if error code is systemic or not
        if contract is not None:
            status_code = errorCode
            status_text = 'Error:' + str(errorCode) + '_' + str(errorString)
            # self.__contracts_db.update_contract_status(
            #     symbol=contract.symbol,
            #     exchange=contract.exchange,
            #     currency=contract.currency,
            #     status_code=status_code,
            #     status_text=status_text)
            print(contract.symbol + '_' + contract.exchange + ' ' + status_text)



    def connect(self,):
        IP = get_config_value('tws_connector', 'ip')
        PORT = int(get_config_value('tws_connector', 'port'))
        self.__ib.connect(host=IP, port=PORT, clientId=1, readonly=True)



    def disconnect(self,):
        self.__ib.disconnect()
        self.__connection_error = False



    def is_connected(self,):
        return self.__ib.isConnected()



    def has_error(self,):
        return self.__connection_error



    def get_historical_data(self, symbol, exchange, currency, duration):
        """
        Description

        Args:
            None

        Returns:
            Nothing

        Raises:
            No errors
        """

        # Create contract
        ib_contract = ib_insync.contract.Stock(
            symbol=symbol,
            exchange=exchange,
            currency=currency)

        # Request data
        print(' Requsting data.', end='')
        bars = self.__ib.reqHistoricalData(
            ib_contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting='1 day',
            whatToShow='ADJUSTED_LAST',
            useRTH=True)
        print(' Receiving completed.', end='')

        if len(bars) == 0:
            print('No data received.', end='')
            print('-------------------------')
            return None

        # Reformatting of received bars
        quotes = []
        for bar in bars:
            quote = (bar.date.strftime('%Y-%m-%d'),
                bar.open,
                bar.high,
                bar.low,
                bar.close,
                bar.volume)
            quotes.append(quote)
        return quotes



    def get_contract_details(self, contract_type_from_listing, broker_symbol,
        exchange, currency):

        debug_string = f"""Getting IB contract details for 
            {broker_symbol}_{exchange}"""
        print(debug_string, end='')
        
        # Create contract object
        ib_contract = ib_insync.contract.Stock(
            symbol=broker_symbol,
            exchange=self.__encode_exchange(exchange),
            currency=currency)

        # Request data and disconnect
        print(' Requsting data.', end='')
        details = self.__ib.reqContractDetails(ib_contract)
        print(' Receiving completed.')

        # Check returned data
        if len(details) > 0:
            details = details[0]
        else:
            print("No details returned.")
            return None

        # Decode exchange names
        details.contract.exchange = \
            self.__decode_exchange(details.contract.exchange)
        details.contract.primaryExchange = \
            self.__decode_exchange(details.contract.primaryExchange)

        return details
