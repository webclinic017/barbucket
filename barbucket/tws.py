# Imports
import logging

import ib_insync

from .config import Config
from .tools import Tools


class Tws():

    def __init__(self):
        # Create connection object
        self.__ib = ib_insync.ib.IB()
        # Register own error handler on ib hook
        self.__ib.errorEvent += self.__on_tws_error

        self.__connection_error = False
        self.__contract_error_status = None
        self.__contract_error_code = None

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

        config = Config()

        # Abort receiving if systematical problem is detected
        NON_SYSTEMIC_CODES = config.get_config_value_single(
            'tws_connector',
            'non_systemic_codes')
        NON_SYSTEMIC_CODES = list(map(int, NON_SYSTEMIC_CODES))
        if errorCode not in NON_SYSTEMIC_CODES:
            logging.error(
                f"Systemic problem in TWS connection detected. {errorCode}: {errorString}")
            self.__connection_error = True

        # Write error info to contract database, if error is related to contract
        if contract is not None:
            self.__contract_error_status = errorString
            self.__contract_error_code = errorCode
            logging.error(
                f"Problem for {contract} detected. {errorCode}: {errorString}")

    def connect(self,):
        config = Config()

        IP = config.get_config_value_single('tws_connector', 'ip')
        PORT = int(config.get_config_value_single('tws_connector', 'port'))
        logging.info(f"Connecting to TWS on {IP}:{PORT}.")
        self.__ib.connect(host=IP, port=PORT, clientId=1, readonly=True)

    def disconnect(self,):
        logging.info("Disconnecting from TWS.")
        self.__ib.disconnect()
        self.__connection_error = False

    def is_connected(self,):
        return self.__ib.isConnected()

    def has_error(self,):
        return self.__connection_error

    def get_contract_error(self,):
        return [self.__contract_error_code, self.__contract_error_status]

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

        self.__contract_error_status = None
        self.__contract_error_code = None

        # Create contract
        ib_contract = ib_insync.contract.Stock(
            symbol=symbol,
            exchange=exchange,
            currency=currency)

        # Request data
        logging.info(
            f"Requesting historical quotes for {exchange}_{symbol}_{currency}_{duration.replace(' ', '')} at TWS.")
        bars = self.__ib.reqHistoricalData(
            ib_contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting='1 day',
            whatToShow='ADJUSTED_LAST',
            useRTH=True)
        logging.info(f"Received {len(bars)} quotes.")

        if len(bars) == 0:
            return None
        else:
            # Reformatting of received bars
            quotes = []
            for bar in bars:
                quote = (
                    contract_id,
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

        # Create contract object
        ib_contract = ib_insync.contract.Stock(
            symbol=broker_symbol,
            exchange=tools.encode_exchange_ib(exchange),
            currency=currency)

        # Request data
        logging.info(
            f"Requesting contract details for {broker_symbol}_{exchange}_{currency} at TWS")
        details = self.__ib.reqContractDetails(ib_contract)

        # Check returned data
        logging.info(f"Received details for {len(details)} contracts.")
        if len(details) > 0:
            details = details[0]
        else:
            return None

        # Decode exchange names
        details.contract.exchange = \
            tools.decode_exchange_ib(details.contract.exchange)
        details.contract.primaryExchange = \
            tools.decode_exchange_ib(details.contract.primaryExchange)

        return details
