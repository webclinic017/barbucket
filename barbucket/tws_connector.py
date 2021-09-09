from typing import Any, List, Tuple
import logging

import ib_insync

from .mediator import Mediator

logger = logging.getLogger(__name__)


class TwsConnector():
    """Provides methods to download data from IB TWS"""

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator
        # Create connection object
        self.__ib = ib_insync.ib.IB()
        # Register own error handler on ib hook
        self.__ib.errorEvent += self.__on_tws_error
        self.__connection_error = False
        self.__contract_error_status = None
        self.__contract_error_code = None

    def __on_tws_error(self, reqId: int, errorCode: int, errorString: str,
                       contract: Any) -> None:
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
        NON_SYSTEMIC_CODES = self.mediator.notify(
            "get_config_value_single",
            {'section': "tws_connector",
             'option': "non_systemic_codes"})
        NON_SYSTEMIC_CODES = list(map(int, NON_SYSTEMIC_CODES))
        if errorCode not in NON_SYSTEMIC_CODES:
            logger.error(f"Systemic problem in TWS connection detected. "
                         f"{errorCode}: {errorString}")
            self.__connection_error = True

        # Write error info to contract database, if error is related to contract
        if contract is not None:
            self.__contract_error_status = errorString
            self.__contract_error_code = errorCode
            logger.error(f"Problem for {contract} detected. {errorCode}: "
                         f"{errorString}")

    def connect(self) -> None:
        IP = self.mediator.notify(
            "get_config_value_single",
            {'section': "tws_connector",
             'option': "ip"})
        PORT = int(self.mediator.notify(
            "get_config_value_single",
            {'section': "tws_connector",
             'option': "port"}))

        self.__ib.connect(host=IP, port=PORT, clientId=1, readonly=True)
        logger.info(f"Connected to TWS on {IP}:{PORT}.")

    def disconnect(self) -> None:
        self.__ib.disconnect()
        self.__connection_error = False
        logger.info("Disconnected from TWS.")

    def is_connected(self) -> Any:
        return self.__ib.isConnected()

    def has_error(self) -> Any:
        return self.__connection_error

    def get_contract_error(self) -> Any:
        return (self.__contract_error_code, self.__contract_error_status)

    def download_historical_quotes(self, contract_id: int, symbol: str,
                                   exchange: str, currency: str, duration: str
                                   ) -> List[Tuple[Any]]:
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
        logger.info(f"Requesting historical quotes for {exchange}_{symbol}_"
                    f"{currency}_{duration.replace(' ', '')} at TWS.")
        bars = self.__ib.reqHistoricalData(
            ib_contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting='1 day',
            whatToShow='ADJUSTED_LAST',
            useRTH=True)
        logger.info(f"Received {len(bars)} quotes.")

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

    def download_contract_details(self, contract_type_from_listing: str,
                                  broker_symbol: str, exchange: str,
                                  currency: str) -> Any:
        """Download details for a contract from IB TWS"""

        # Create contract object
        ex = self.mediator.notify(
            "encode_exchange_ib",
            {'exchange': exchange})
        ib_contract = ib_insync.contract.Stock(
            symbol=broker_symbol,
            exchange=ex,
            currency=currency)

        # Request data
        logger.info(f"Requesting contract details for {broker_symbol}_"
                    f"{exchange}_{currency} at TWS")
        details = self.__ib.reqContractDetails(ib_contract)

        # Check returned data
        logger.info(f"Received details for {len(details)} contracts.")

        return details
