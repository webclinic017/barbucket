import logging
from typing import Any, List
from datetime import date, timedelta

import numpy as np
import enlighten
from ib_insync.wrapper import RequestError

from .signal_handler import SignalHandler
from .encoder import Encoder
from .config_reader import ConfigReader
from .contracts_db_connector import ContractsDbConnector
from .universes_db_connector import UniversesDbConnector
from .quotes_db_connector import QuotesDbConnector
from .quotes_status_db_connector import QuotesStatusDbConnector
from .tws_connector import TwsConnector


logger = logging.getLogger(__name__)


class IbQuotesProcessor():
    """Provides methods to download historical quotes from TWS."""

    def __init__(self) -> None:
        self.__contracts_db_connector = ContractsDbConnector()
        self.__universes_db_connector = UniversesDbConnector()
        self.__quotes_db_connector = QuotesDbConnector()
        self.__quotes_status_db_connector = QuotesStatusDbConnector()
        self.__tws_connector = TwsConnector()
        self.__signal_handler = SignalHandler()
        self.__config_reader = ConfigReader()
        self.__contract_id = None
        self.__contract_data = None
        self.__quotes_status = None
        self.__duration = None
        self.__quotes_from = None
        self.__quotes_till = None
        manager = enlighten.get_manager()  # Setup progress bar
        self.__pbar = manager.counter(
            total=0,
            desc="Contracts", unit="contracts")

    def download_historical_quotes(self, universe: str) -> None:
        """Download historical quotes from TWS"""

        contract_ids = self.__get_contracts(universe)
        self.__pbar.total = len(contract_ids)
        self.__connect_tws()
        try:
            for self.__contract_id in contract_ids:
                if self.__signal_handler.exit_requested():
                    raise ExitSignalDetectedError("Message")
                self.__get_contract_data()
                self.__get_contract_status()
                try:
                    self.__calculate_dates()
                except (QuotesDurationError, ContractHasErrorStatusError):
                    # Decrement total, as these contracts add almost nothing to time
                    self.__pbar.total -= 1
                    self.__pbar.update(incr=0)
                    continue
                try:
                    bar_data = self.__get_quotes_from_tws()
                except RequestError as e:
                    logger.info(e)
                    if e.reqId != -1:
                        self.__update_quotes_status(
                            error=True,
                            status_code=e.code,
                            status_text=e.message)
                        self.__pbar.update(incr=1)
                    continue
                else:
                    self.__write_quotes_to_db(bar_data)
                    self.__update_quotes_status(error=False)
                    self.__pbar.update(incr=1)
        except ExitSignalDetectedError:
            pass
        else:
            logger.info(
                f"Finished downloading historical data for universe '"
                f"{universe}'")
        finally:
            self.__disconnect_tws()

    def __get_contracts(self, universe: str) -> List[int]:
        return self.__universes_db_connector.get_universe_members(
            universe=universe)

    def __connect_tws(self) -> None:
        self.__tws_connector.connect()

    def __get_contract_data(self) -> None:
        filters = {'contract_id': self.__contract_id}
        return_columns = ['broker_symbol', 'exchange', 'currency']
        contract_data = self.__contracts_db_connector.get_contracts(
            filters=filters,
            return_columns=return_columns)
        self.__contract_data = contract_data[0]

    def __get_contract_status(self) -> None:
        self.__quotes_status = self.__quotes_status_db_connector.get_quotes_status(
            contract_id=self.__contract_id)

    def __calculate_dates(self) -> None:
        print(self.__quotes_status['status_code'])
        if self.__quotes_status['status_code'] == 0:
            self.__calculate_dates_for_new_contract()
        elif self.__quotes_status['status_code'] == 1:
            self.__calculate_dates_for_existing_contract()
        else:
            # self.__contract_has_error_status()
            self.__calculate_dates_for_new_contract()  # Test
        logger.debug(f"Calculated 'duration' as: {self.__duration}, "
                     f"'from' as: {self.__quotes_from}, "
                     f"'till' as: {self.__quotes_till}")

    def __calculate_dates_for_new_contract(self) -> None:
        self.__duration = "15 Y"
        from_date = date.today() - timedelta(days=5479)  # 15 years
        self.__quotes_from = from_date.strftime('%Y-%m-%d')
        self.__quotes_till = date.today().strftime('%Y-%m-%d')

    def __calculate_dates_for_existing_contract(self) -> None:
        """Calculate, how many days need to be downloaded"""

        # Get config constants
        REDOWNLOAD_DAYS = int(self.__config_reader.get_config_value_single(
            section="quotes",
            option="redownload_days"))
        OVERLAP_DAYS = int(self.__config_reader.get_config_value_single(
            section="quotes",
            option="overlap_days"))

        start_date = (self.__quotes_status['daily_quotes_requested_till'])
        end_date = date.today().strftime('%Y-%m-%d')
        ndays = np.busday_count(start_date, end_date)
        if ndays <= REDOWNLOAD_DAYS:
            message = f"Existing data is only {ndays} days old."
            logger.info(message)
            raise QuotesDurationError(message)
        if ndays > 360:
            message = f"Existing data is already {ndays} days old."
            logger.info(message)
            raise QuotesDurationError(message)
        ndays += OVERLAP_DAYS
        self.__duration = str(ndays) + " D"
        self.__quotes_from = self.__quotes_status['daily_quotes_requested_from']
        self.__quotes_till = end_date

    def __contract_has_error_status(self) -> None:
        message = "Contract already has error status. Skipped."
        logger.info(message)
        raise ContractHasErrorStatusError(message)

    def __get_quotes_from_tws(self) -> List[Any]:
        """Download quotes for one contract from TWS"""
        exchange = Encoder.encode_exchange_ib(self.__contract_data['exchange'])
        quotes = self.__tws_connector.download_historical_quotes(
            symbol=self.__contract_data['broker_symbol'],
            exchange=exchange,
            currency=self.__contract_data['currency'],
            duration=self.__duration)
        return quotes

    def __update_quotes_status(
            self,
            error: bool,
            status_code: int = None,
            status_text: str = None) -> None:
        if error:
            code = status_code
            text = status_text
            q_from = "NULL"
            q_till = "NULL"
        else:
            code = 1
            text = "Successful"
            q_from = self.__quotes_from
            q_till = self.__quotes_till
        self.__quotes_status_db_connector.update_quotes_status(
            contract_id=self.__contract_id,
            status_code=code,
            status_text=text,
            daily_quotes_requested_from=q_from,
            daily_quotes_requested_till=q_till)

    def __write_quotes_to_db(self, bar_data) -> None:
        quotes = []
        for bar in bar_data:
            quote = (
                self.__contract_id,
                bar.date.strftime('%Y-%m-%d'),
                bar.open,
                bar.high,
                bar.low,
                bar.close,
                bar.volume)
            quotes.append(quote)
        self.__quotes_db_connector.insert_quotes(quotes=quotes)

    def __disconnect_tws(self) -> None:
        self.__tws_connector.disconnect()


class QuotesDurationError(Exception):
    """Docstring"""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)


class ContractHasErrorStatusError(Exception):
    """Docstring"""
# TODO

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)


class ExitSignalDetectedError(Exception):
    """"Doc"""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)
