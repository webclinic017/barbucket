from typing import Any, List
import logging

from ib_insync.ib import IB
from ib_insync.objects import BarDataList
from ib_insync.contract import Stock, ContractDetails

from .encodings import Api, Exchange, ContractType, Symbol
from .config_reader import ConfigReader


logger = logging.getLogger(__name__)


class TwsConnector():
    """Provides methods to download data from IB TWS"""

    def __init__(self) -> None:
        self.__config_reader = ConfigReader()
        self.__ib = IB()  # Create connection objec
        self.__ib.RaiseRequestErrors = True  # Enable exceptions
        logging.getLogger("ib_insync").setLevel(
            logging.WARN)  # todo: change with verbosity level option

    def connect(self) -> None:
        """Connect to TWS"""

        IP = self.__config_reader.get_config_value_single(
            section="tws_connector",
            option="ip")
        PORT = int(self.__config_reader.get_config_value_single(
            section="tws_connector",
            option="port"))
        self.__ib.connect(host=IP, port=PORT, clientId=1, readonly=True)
        logger.debug(f"Connected to TWS on {IP}:{PORT}.")

    def disconnect(self) -> None:
        """Disconnect from TWS"""

        self.__ib.disconnect()
        logger.debug("Disconnected from TWS.")

    def download_historical_quotes(
            self,
            symbol: str,
            exchange: str,
            currency: str,
            duration: str) -> BarDataList:
        """Download historical quotes for a contract from IB TWS

        :param symbol: Contracts symbol
        :type symbol: str
        :param exchange: Contracts exchange
        :type exchange: str
        :param currency: Contracts currency
        :type currency: str
        :param duration: Duration to download
        :type duration: str
        :return: 
        :rtype: ib_insync.objects.BarDataList
        """

        exchange = Exchange.encode(name=exchange, to_api=Api.IB)
        symbol = Symbol.encode(name=symbol, to_api=Api.IB)
        ib_contract = Stock(
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

    def download_contract_details(self, broker_symbol: str, exchange: str,
                                  currency: str) -> List[ContractDetails]:
        """Download details for a contract from IB TWS

        :param symbol: Contracts symbol
        :type symbol: str
        :param exchange: Contracts exchange
        :type exchange: str
        :param currency: Contracts currency
        :type currency: str
        :return: Details object for the contract from IB TWS
        :rtype: ib_insync.contract.ContractDetails
        """

        exchange = Exchange.encode(name=exchange, to_api=Api.IB)
        symbol = Symbol.encode(name=broker_symbol, to_api=Api.IB)
        ib_contract = Stock(
            symbol=symbol,
            exchange=exchange,
            currency=currency)
        details = self.__ib.reqContractDetails(ib_contract)
        self.__validate_details(
            details=details,
            broker_symbol=broker_symbol,
            exchange=exchange,
            currency=currency)
        logger.debug(
            f"Received contract details for {broker_symbol}_{exchange}_"
            f"{currency} from TWS")
        return self.__decode_details(details[0])

    def __validate_details(
            self,
            details: List[ContractDetails],
            broker_symbol: str,
            exchange: str,
            currency: str) -> None:
        if details is None:
            raise IbDetailsInvalidError(
                f"Result for {broker_symbol}_{exchange}_{currency} is None")
        elif len(details) == 0:
            raise IbDetailsInvalidError(
                f"Result for {broker_symbol}_{exchange}_{currency} is []")
        elif len(details) > 1:
            raise IbDetailsInvalidError(
                f"Multiple results for {broker_symbol}_{exchange}_{currency}")

    def __decode_details(self, details: ContractDetails) -> ContractDetails:
        details.contract.exchange = Exchange.decode(
            name=details.contract.exchange,
            from_api=Api.IB)
        details.contract.primaryExchange = Exchange.decode(
            name=details.contract.primaryExchange,
            from_api=Api.IB)
        details.stockType = ContractType.decode(
            name=details.stockType,
            from_api=Api.IB)
        return details


class IbDetailsInvalidError(Exception):
    """"Doc"""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)
