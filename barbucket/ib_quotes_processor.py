import logging
from pathlib import Path
from os import path, listdir
from typing import Any, List, Dict, Tuple
from datetime import date, timedelta

import pandas as pd
import numpy as np
import enlighten

from .mediator import Mediator
from .custom_exceptions import ExistingDataIsSufficientError
from .custom_exceptions import ExistingDataIsTooOldError
from .custom_exceptions import ContractHasErrorStatusError
from .custom_exceptions import QueryReturnedMultipleResultsError
from .custom_exceptions import QueryReturnedNoResultError
from .base_component import BaseComponent


class IbQuotesProcessor(BaseComponent):
    """Docstring"""

    def __init__(self, mediator: Mediator = None) -> None:
        logging.info(f"Message")
        self.mediator = mediator
        self.__contract_id = None
        self.__contract_data = None
        self.__contract_status = None
        self.__duration = None
        self.__quotes_from = None
        self.__quotes_till = None

        # Setup progress bar
        manager = enlighten.get_manager()
        self.__pbar = manager.counter(
            total=0,
            desc="Contracts", unit="contracts")

    def download_historical_quotes(self, universe):
        """Docstring"""

        logging.info(f"Fetching historical quotes for universe {universe}.")
        contract_ids = self.__get_contracts(universe)
        self.__pbar.total = len(contract_ids)
        self.__connect_tws()
        try:
            for self.__contract_id in contract_ids:
                if self.__check_abort_conditions():
                    break
                try:
                    self.__get_contract_data()
                    self.__get_contract_status()
                except (QueryReturnedNoResultError,
                        QueryReturnedMultipleResultsError):
                    self.__pbar.total -= 1
                    self.__pbar.update(incr=0)
                    continue
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
                except QueryReturnedNoResultError:
                    self.__write_error_status_to_db()
                else:
                    self.__write_quotes_to_db(quotes)
                    self.__write_success_status_to_db()
                self.__pbar.update()
        finally:
            self.__disconnect_tws()

    def __get_contracts(self, universe) -> List[int]:
        """Docstring"""
        logging.info(f"Message")
        return self.mediator.notify(
            "get_universe_members",
            {'universe': universe})

    def __connect_tws(self) -> None:
        """Docstring"""
        logging.info(f"Message")
        self.mediator.notify("connect_to_tws")
        logging.info(f"Connnected to TWS.")

    def __disconnect_tws(self) -> None:
        """Docstring"""
        logging.info(f"Message")
        self.mediator.notify("disconnect_from_tws")
        logging.info(f"Disconnnected from TWS.")

    def __check_abort_conditions(self) -> bool:
        """Docstring"""
        logging.info(f"Message")
        if self.mediator.notify("exit_signal"):
            logging.info(f"Ctrl-C detected. Abort fetching of IB "
                         "details.")
            return True
        elif self.mediator.notify("tws_has_error"):
            logging.info(f"TWS error detected. Abort fetching of IB "
                         "details.")
            return True
        else:
            return False

    def __get_contract_data(self) -> None:
        """Get contracts data"""
        logging.info(f"Message")
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
        """Get contracts status"""
        logging.info(f"Message")
        self.__contract_status = self.mediator.notify(
            "get_quotes_status",
            {'contract_id': self.__contract_id})

    def __calculate_dates(self) -> None:
        """Docstring"""
        logging.info(f"Message")
        if self.__contract_status['status_code'] == 0:
            self.__calculate_dates_for_new_contract()
        elif self.__contract_status['status_code'] == 1:
            self.__calculate_dates_for_existing_contract()
        else:
            self.__contract_has_error_status()

    def __calculate_dates_for_new_contract(self) -> None:
        """Docstring"""
        logging.info(f"Message")
        self.__duration = "15 Y"
        from_date = date.today() - timedelta(days=5479)  # 15 years
        self.__quotes_from = from_date.strftime('%Y-%m-%d')
        self.__quotes_till = date.today().strftime('%Y-%m-%d')

    def __calculate_dates_for_existing_contract(self) -> None:
        """Docstring"""
        logging.info(f"Message")

        # Get config constants
        REDOWNLOAD_DAYS = int(self.mediator.notify(
            "get_config_value_single",
            {'section': "quotes", 'option': "redownload_days"}))
        OVERLAP_DAYS = int(self.mediator.notify(
            "get_config_value_single",
            {'section': "quotes", 'option': "overlap_days"}))

        start_date = (self.__contract_status['daily_quotes_requested_till'])
        end_date = date.today().strftime('%Y-%m-%d')
        ndays = np.busday_count(start_date, end_date)
        if ndays <= REDOWNLOAD_DAYS:
            logging.info(f"Existing data is only {ndays} days old.")
            raise ExistingDataIsSufficientError
        if ndays > 360:
            logging.info(f"Existing data is already {ndays} days old.")
            raise ExistingDataIsTooOldError
        ndays += OVERLAP_DAYS
        self.__duration = str(ndays) + " D"
        self.__quotes_from = self.__contract_status['daily_quotes_requested_from']
        self.__quotes_till = end_date

    def __contract_has_error_status(self) -> None:
        """Docstring"""
        logging.info("Contract already has error status. Skipped.")
        raise ContractHasErrorStatusError

    def __get_quotes_from_tws(self) -> List[Any]:
        """Docstring"""
        logging.info(f"Message")
        exchange = self.mediator.notify(
            "encode_exchange_ib",
            {'exchange': self.__contract_data['exchange']})
        parameters = {
            'contract_id': self.__contract_id,
            'symbol': self.__contract_data['broker_symbol'],
            'exchange': exchange,
            'currency': self.__contract_data['currency'],
            'duration': self.__duration}
        return self.mediator.notify("download_historical_quotes", parameters)

    def __write_quotes_to_db(self, quotes) -> None:
        """Inserting quotes into database"""
        logging.info(f"Storing {len(quotes)} quotes to database.")
        self.mediator.notify("insert_quotes", {'quotes': quotes})

    def __write_success_status_to_db(self):
        """Docstring"""
        logging.info(f"Message")
        parameters = {
            'contract_id': self.__contract_id,
            'status_code': 1,
            'status_text': "Successful",
            'daily_quotes_requested_from': self.__quotes_from,
            'daily_quotes_requested_till': self.__quotes_till}
        self.mediator.notify("insert_quotes_status", parameters)

    def __write_error_status_to_db(self) -> None:
        """Docstring"""
        logging.info(f"Message")
        # Write error info to contracts database
        (error_code, error_text) = self.mediator.notify(
            "get_tws_contract_error", {})
        parameters = {
            'contract_id': self.__contract_id,
            'status_code': error_code,
            'status_text': error_text,
            'daily_quotes_requested_from': None,
            'daily_quotes_requested_till': None}
        self.mediator.notify("insert_quotes_status", parameters)
