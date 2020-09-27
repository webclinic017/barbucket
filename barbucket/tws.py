# Imports
import ib_insync
import pandas as pd
import numpy as np

from barbucket.config import get_config_value
from barbucket.tools import Tools


class Tws():

    def __init__(self):
        # Create connection object
        self.__ib = ib_insync.ib.IB()
        # Register own error handler on ib hook
        self.__ib.errorEvent += self.__on_tws_error

        self.__connection_error = False


    def __on_tws_error(self, reqId, errorCode, errorString, contract):
        """
        Is called from 'ib_insync' as callback on errors and writes error
        details to quotes_status in database.

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


    def download_historical_quotes(self, contract_id, symbol, exchange,
        currency, duration):
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
            quote = (contract_id,
                bar.date.strftime('%Y-%m-%d'),
                bar.open,
                bar.high,
                bar.low,
                bar.close,
                bar.volume)
            quotes.append(quote)
        return quotes


    def download_contract_details(self, contract_type_from_listing,
        broker_symbol, exchange, currency):

        tools = Tools()

        debug_string = f"Getting IB contract details for {broker_symbol}_{exchange}"
        print(debug_string, end='')
        
        # Create contract object
        ib_contract = ib_insync.contract.Stock(
            symbol=broker_symbol,
            exchange=tools.encode_exchange_ib(exchange),
            currency=currency)

        # Request data
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
            tools.decode_exchange_ib(details.contract.exchange)
        details.contract.primaryExchange = \
            tools.decode_exchange_ib(details.contract.primaryExchange)

        return details
