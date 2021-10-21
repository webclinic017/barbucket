from typing import Any, List, Tuple, Dict
import logging

import ib_insync

from .encodings import Api, Exchange
from .config_reader import ConfigReader


logger = logging.getLogger(__name__)


class TwsConnector():
    """Provides methods to download data from IB TWS"""

    def __init__(self) -> None:
        self.__config_reader = ConfigReader()
        self.__ib = ib_insync.ib.IB()  # Create connection objec
        self.__ib.RaiseRequestErrors = True  # Enable exceptions
        logging.getLogger("ib_insync").setLevel(
            logging.WARN)  # todo: change with verbosity level option

    def connect(self) -> None:
        IP = self.__config_reader.get_config_value_single(
            section="tws_connector",
            option="ip")
        PORT = int(self.__config_reader.get_config_value_single(
            section="tws_connector",
            option="port"))

        self.__ib.connect(host=IP, port=PORT, clientId=1, readonly=True)
        logger.debug(f"Connected to TWS on {IP}:{PORT}.")

    def disconnect(self) -> None:
        self.__ib.disconnect()
        logger.debug("Disconnected from TWS.")

    def download_historical_quotes(
            self, symbol: str, exchange: str, currency: str, duration: str
    ) -> List[Tuple[Any]]:
        """Download historical quotes from IB TWS"""

        ib_contract = ib_insync.contract.Stock(
            symbol=symbol,
            exchange=exchange,
            currency=currency)
        bar_data = self.__ib.reqHistoricalData(
            contract=ib_contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting='1 day',
            whatToShow='ADJUSTED_LAST',
            useRTH=True)
        logger.debug(
            f"Received {len(bar_data)} quotes for {exchange}_{symbol}_"
            f"{currency}_{duration.replace(' ', '')} from TWS.")
        return bar_data

    def download_contract_details(
            self, broker_symbol: str, exchange: str, currency: str) -> Any:
        """Download details for a contract from IB TWS"""

        ex = Exchange.encode(
            name=exchange,
            to_api=Api.IB)
        ib_contract = ib_insync.contract.Stock(
            symbol=broker_symbol,
            exchange=ex,
            currency=currency)
        details = self.__ib.reqContractDetails(ib_contract)
        logger.debug(
            f"Received contract details for {broker_symbol}_{exchange}_"
            f"{currency} from TWS")
        return details
