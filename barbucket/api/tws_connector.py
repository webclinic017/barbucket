from typing import List
import logging

from ib_insync.ib import IB
from ib_insync.contract import Stock, ContractDetails

from barbucket.config.config_reader import ConfigReader
from barbucket.domain_model.data_classes import Contract, Quote, ContractDetailsIb
from barbucket.domain_model.types import Api, Exchange, TickerSymbol, ApiNotationTranslator, Api
from barbucket.util.custom_exceptions import InvalidDataReceivedError

logger = logging.getLogger(__name__)


class TwsConnector():
    """Provides methods to download data from IB TWS"""

    def __init__(self, config_reader: ConfigReader) -> None:
        self._config_reader = config_reader
        self._ib = IB()  # Create connection objec
        self._ib.RaiseRequestErrors = True  # Enable exceptions
        logging.getLogger("ib_insync").setLevel(
            logging.WARN)  # todo: change with verbosity level option

    def connect(self) -> None:
        """Connect to TWS"""

        IP = self._config_reader.get_config_value_single(
            section="tws_connector",
            option="ip")
        PORT = int(self._config_reader.get_config_value_single(
            section="tws_connector",
            option="port"))
        self._ib.connect(host=IP, port=PORT, clientId=1, readonly=True)
        logger.debug(f"Connected to TWS on '{IP}:{PORT}'.")

    def disconnect(self) -> None:
        """Disconnect from TWS"""

        self._ib.disconnect()
        logger.debug("Disconnected from TWS.")

    def download_historical_quotes(
            self, contract: Contract, duration: str) -> List[Quote]:
        """Download historical quotes for a contract from IB TWS"""

        ib_contract = self._create_ib_contract(contract)

        # Download quotes
        ib_quotes = self._ib.reqHistoricalData(
            contract=ib_contract,
            endDateTime='',
            durationStr=duration,
            barSizeSetting='1 day',
            whatToShow='ADJUSTED_LAST',
            useRTH=True)
        logger.debug(
            f"Received {len(ib_quotes)} quotes for '{contract}' with "
            f"timeframe '{duration.replace(' ', '')}' from TWS.")

        # Reformat recieved data
        quotes_list = []
        for ib_quote in ib_quotes:
            quote = Quote(
                contract=contract,
                date=ib_quote.date,
                open=ib_quote.open,
                high=ib_quote.high,
                low=ib_quote.low,
                close=ib_quote.close,
                volume=ib_quote.volume)
            quotes_list.append(quote)
        return quotes_list

    def download_contract_details(self, contract: Contract) -> ContractDetailsIb:
        """Download details for a contract from IB TWS
        """

        ib_contract = self._create_ib_contract(contract)
        ib_details = self._ib.reqContractDetails(ib_contract)
        self._validate_details(contract=contract, details=ib_details)
        logger.debug(
            f"Received contract_details for '{contract}' from TWS")
        stock_type_from_details = ApiNotationTranslator.get_stock_type_from_api_notation(
            name=ib_details[0].stockType, api=Api.IB)
        primary_exchange = ApiNotationTranslator.get_exchange_from_api_notation(
            name=ib_details[0].contract.primaryExchange, api=Api.IB)
        details = ContractDetailsIb(
            contract=contract,
            stock_type_from_details=stock_type_from_details,
            primary_exchange=primary_exchange,
            industry=ib_details[0].industry,
            category=ib_details[0].category,
            subcategory=ib_details[0].subcategory)
        return details

    # ~~~~~~~~~~~~~~~~~~~~ private methods ~~~~~~~~~~~~~~~~~~~~

    def _create_ib_contract(self, contract: Contract) -> Stock:
        exchange = Exchange[contract.exchange]
        ib_exchange = ApiNotationTranslator.get_api_notation_for_exchange(
            exchange=exchange, api=Api.IB)
        symbol = TickerSymbol(name=contract.broker_symbol)
        ib_symbol = ApiNotationTranslator.get_api_notation_for_ticker_symbol(
            ticker_symbol=symbol, api=Api.IB)
        ib_contract = Stock(
            symbol=ib_symbol,
            exchange=ib_exchange,
            currency=contract.currency)
        return ib_contract

    def _validate_details(self, contract: Contract, details: List[ContractDetails]) -> None:
        if details is None:
            raise InvalidDataReceivedError(
                f"Ib cont result for '{contract}' is None")
        elif len(details) == 0:
            raise InvalidDataReceivedError(
                f"Result for '{contract}' is []")
        elif len(details) > 1:
            raise InvalidDataReceivedError(
                f"Multiple results for '{contract}'")
