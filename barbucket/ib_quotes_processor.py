import logging
from typing import Any, List
from datetime import date, timedelta
from sqlite3 import Row

import numpy as np
import enlighten
from ib_insync.wrapper import RequestError
from ib_insync.objects import BarDataList

from .signal_handler import SignalHandler, ExitSignalDetectedError
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
        self.__contract_id: int
        self.__contract_data: Row
        self.__quotes_status: Row
        self.__duration: str
        self.__quotes_from: str
        self.__quotes_till: str
        manager = enlighten.get_manager()  # Setup progress bar
        self.__pbar = manager.counter(
            total=0,
            desc="Contracts", unit="contracts")

    def download_historical_quotes(self, universe: str) -> None:
        """Download historical quotes from TWS

        :param universe: Universe to download quotes for
        :type universe: str
        """

        contract_ids = self.__get_contracts(universe)
        self.__pbar.total = len(contract_ids)
        self.__tws_connector.connect()
        try:
            for self.__contract_id in contract_ids:
                self.__signal_handler.is_exit_requested()
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
                f"Finished downloading historical data for universe "
                f"'{universe}'")
        finally:
            self.__tws_connector.disconnect()

    def __get_contracts(self, universe: str) -> List[int]:
        return self.__universes_db_connector.get_universe_members(
            universe=universe)

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
        """Calculate 'from' and 'to' dates for quotes to be downloaded"""

        if self.__quotes_status['status_code'] == 0:
            self.__calculate_dates_for_new_contract()
        elif self.__quotes_status['status_code'] == 1:
            self.__calculate_dates_for_existing_contract()
        else:
            self.__contract_has_error_status()
        logger.debug(f"Calculated 'duration' as: {self.__duration}, "
                     f"'from' as: {self.__quotes_from}, "
                     f"'till' as: {self.__quotes_till}")

    def __calculate_dates_for_new_contract(self) -> None:
        self.__duration = "15 Y"
        from_date = date.today() - timedelta(days=5479)  # 15 years
        self.__quotes_from = from_date.strftime('%Y-%m-%d')
        self.__quotes_till = date.today().strftime('%Y-%m-%d')

    def __calculate_dates_for_existing_contract(self) -> None:
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
            message = (
                f"Skipping {self.__contract_data['broker_symbol']}, existing "
                f"data is only {ndays} days old.")
            logger.debug(message)
            raise QuotesDurationError(message)
        if ndays > 360:
            message = (
                f"Skipping {self.__contract_data['broker_symbol']}, existing "
                f"data is already {ndays} days old.")
            logger.debug(message)
            raise QuotesDurationError(message)
        ndays += OVERLAP_DAYS
        self.__duration = str(ndays) + " D"
        self.__quotes_from = self.__quotes_status['daily_quotes_requested_from']
        self.__quotes_till = end_date

    def __contract_has_error_status(self) -> None:
        message = f"{self.__contract_data['broker_symbol']} already has error status. Skipped."
        logger.debug(message)
        raise ContractHasErrorStatusError(message)

    def __get_quotes_from_tws(self) -> BarDataList:
        quotes = self.__tws_connector.download_historical_quotes(
            symbol=self.__contract_data['broker_symbol'],
            exchange=self.__contract_data['exchange'],
            currency=self.__contract_data['currency'],
            duration=self.__duration)
        return quotes

    def __update_quotes_status(
            self,
            error: bool,
            status_code: int = 0,
            status_text: str = "") -> None:
        if error:
            self.__quotes_status_db_connector.update_quotes_status(
                contract_id=self.__contract_id,
                status_code=status_code,
                status_text=status_text,
                daily_quotes_requested_from="NULL",
                daily_quotes_requested_till="NULL")
        else:
            self.__quotes_status_db_connector.update_quotes_status(
                contract_id=self.__contract_id,
                status_code=1,
                status_text="Successful",
                daily_quotes_requested_from=self.__quotes_from,
                daily_quotes_requested_till=self.__quotes_till)

    def __write_quotes_to_db(self, bar_data: BarDataList) -> None:
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


class QuotesDurationError(Exception):
    """Problem occured with the 'from' and 'to' dates for downloading"""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)


class ContractHasErrorStatusError(Exception):
    """Contract has had an error on previous quotes download attempt"""
# TODO

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)
