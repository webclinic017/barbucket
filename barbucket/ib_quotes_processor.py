import logging
from pathlib import Path
from os import path, listdir
from typing import Any, List, Dict, Tuple
from datetime import date, timedelta

import pandas as pd
import numpy as np
import enlighten

from .mediator import Mediator
from .signal_handler import SignalHandler
from .base_component import BaseComponent
from .encoder import Encoder
from .config_reader import ConfigReader
from .custom_exceptions import (
    ExistingDataIsSufficientError,
    ExistingDataIsTooOldError,
    ContractHasErrorStatusError,
    QueryReturnedMultipleResultsError,
    QueryReturnedNoResultError,
    TwsSystemicError,
    TwsContractRelatedError,
    ExitSignalDetectedError)

logger = logging.getLogger(__name__)


class IbQuotesProcessor(BaseComponent):
    """Provides methods to download historical quotes from TWS."""

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator
        self.__signal_handler = SignalHandler()
        self.__config_reader = ConfigReader()
        self.__contract_id = None
        self.__contract_data = None
        self.__quotes_status = None
        self.__duration = None
        self.__quotes_from = None
        self.__quotes_till = None
        # Setup progress bar
        manager = enlighten.get_manager()
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
                self.__check_abort_signal()
                try:
                    self.__get_contract_data()
                except (QueryReturnedNoResultError,
                        QueryReturnedMultipleResultsError):
                    self.__pbar.total -= 1
                    self.__pbar.update(incr=0)
                    continue
                try:
                    self.__get_contract_status()
                except QueryReturnedNoResultError:
                    print("QueryReturnedNoResultError")  # Todo
                except QueryReturnedMultipleResultsError:
                    print("QueryReturnedMultipleResultsError")  # Todo
                try:
                    self.__calculate_dates()
                except (ExistingDataIsSufficientError,
                        ExistingDataIsTooOldError,
                        ContractHasErrorStatusError):
                    self.__pbar.total -= 1
                    self.__pbar.update(incr=0)
                    continue
                try:
                    quotes = self.__get_quotes_from_tws()
                except TwsContractRelatedError as e:
                    self.__handle_tws_contract_related_error(e)
                except QueryReturnedNoResultError as e:
                    print("This needs to be done.")  # Todo
                    raise e
                else:
                    self.__write_quotes_to_db(quotes)
                    self.__write_success_status_to_db()
                self.__pbar.update(incr=1)
        except TwsSystemicError as e:
            self.__handle_tws_systemic_error(e)
        except ExitSignalDetectedError as e:
            self.__handle_exit_signal_detected_error(e)
        else:
            self.mediator.notify(
                "show_cli_message", {
                    'message': f"Finished downloading historical data for "
                    f"universe '{universe}'"})
        finally:
            self.__disconnect_tws()

    def __get_contracts(self, universe: str) -> List[int]:
        return self.mediator.notify(
            "get_universe_members",
            {'universe': universe})

    def __connect_tws(self) -> None:
        self.mediator.notify("connect_to_tws")

    def __disconnect_tws(self) -> None:
        self.mediator.notify("disconnect_from_tws")

    def __check_abort_signal(self) -> None:
        """Check for abort signal."""
        if self.__signal_handler.exit_requested():
            raise ExitSignalDetectedError

    def __handle_exit_signal_detected_error(self, e) -> None:
        self.mediator.notify("show_cli_message", {'message': "Stopped."})

    def __get_contract_data(self) -> None:
        filters = {'contract_id': self.__contract_id}
        columns = ['broker_symbol', 'exchange', 'currency']
        contract_data = self.mediator.notify(
            "get_contracts",
            {'filters': filters, 'return_columns': columns})
        if len(contract_data) == 0:
            raise QueryReturnedNoResultError
        elif len(contract_data) > 1:
            raise QueryReturnedMultipleResultsError
        else:
            self.__contract_data = contract_data[0]

    def __get_contract_status(self) -> None:
        self.__quotes_status = self.mediator.notify(
            "get_quotes_status",
            {'contract_id': self.__contract_id})

    def __calculate_dates(self) -> None:
        if self.__quotes_status['status_code'] == 0:
            self.__calculate_dates_for_new_contract()
        elif self.__quotes_status['status_code'] == 1:
            self.__calculate_dates_for_existing_contract()
        else:
            self.__contract_has_error_status()
        logger.debug(f"Calculated 'duration' as: {self.__duration}"
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
            logger.debug(f"Existing data is only {ndays} days old.")
            raise ExistingDataIsSufficientError
        if ndays > 360:
            logger.debug(f"Existing data is already {ndays} days old.")
            raise ExistingDataIsTooOldError
        ndays += OVERLAP_DAYS
        self.__duration = str(ndays) + " D"
        self.__quotes_from = self.__quotes_status['daily_quotes_requested_from']
        self.__quotes_till = end_date

    def __contract_has_error_status(self) -> None:
        logger.debug("Contract already has error status. Skipped.")
        raise ContractHasErrorStatusError

    def __get_quotes_from_tws(self) -> List[Any]:
        """Download quotes for one contract from TWS"""
        exchange = Encoder.encode_exchange_ib(self.__contract_data['exchange'])
        parameters = {
            'contract_id': self.__contract_id,
            'symbol': self.__contract_data['broker_symbol'],
            'exchange': exchange,
            'currency': self.__contract_data['currency'],
            'duration': self.__duration}
        return self.mediator.notify("download_historical_quotes", parameters)

    def __write_quotes_to_db(self, quotes) -> None:
        self.mediator.notify("insert_quotes", {'quotes': quotes})

    def __write_success_status_to_db(self):
        parameters = {
            'contract_id': self.__contract_id,
            'status_code': 1,
            'status_text': "Successful",
            'daily_quotes_requested_from': self.__quotes_from,
            'daily_quotes_requested_till': self.__quotes_till}
        self.mediator.notify("insert_quotes_status", parameters)

    def __handle_tws_contract_related_error(self, e):
        logger.warning(f"Contract-related problem in TWS detected: "
                       f"{e.req_id}, {e.contract}, "
                       f"{e.error_code}, {e.error_string}")
        self.mediator.notify(
            "show_cli_message",
            {'message': (f"Request {e.req_id} for contract {e.contract} "
                         f"returned error {e.error_code}: {e.error_string}")})
        parameters = {
            'contract_id': self.__contract_id,
            'status_code': e.error_code,
            'status_text': e.error_string,
            'daily_quotes_requested_from': None,
            'daily_quotes_requested_till': None}
        self.mediator.notify("insert_quotes_status", parameters)

    def __handle_tws_systemic_error(self, e):
        logger.error(f"Systemic problem in TWS connection detected: "
                     f"{e.req_id}, {e.contract}, "
                     f"{e.error_code}, {e.error_string}")
        self.mediator.notify(
            "show_cli_message",
            {'message': (f"Request {e.req_id} for contract {e.contract} "
                         f"returned error {e.error_code}: {e.error_string}")})
