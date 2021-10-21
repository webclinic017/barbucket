import logging
from typing import Any, List

from .contracts_db_connector import ContractsDbConnector
from .ib_exchange_listing_reader import (
    IbExchangeListingSinglepageReader,
    IbExchangeListingMultipageReader,
    WebscrapingReturnedNoResultError,
    ExitSignalDetectedError)


logger = logging.getLogger(__name__)


class IbExchangeListingsProcessor():
    """Provides methods to sync local exchange listings to the IB website."""

    def __init__(self) -> None:
        self.__contracts_db_connector = ContractsDbConnector()
        self.__ctype: str = None
        self.__exchange: str = None
        self.__website_contracts: List[Any] = []
        self.__database_contracts: List[Any] = []

    def sync_contracts_to_listing(self, ctype: str, exchange: str) -> None:
        """Sync local exchange listings to the IB website"""

        self.__ctype = ctype
        self.__exchange = exchange

        pagetypes = {
            'STOCK': "paginated",
            'ETF': "single"
        }

        if pagetypes[ctype] == "single":
            scraper = IbExchangeListingSinglepageReader()
        elif pagetypes[ctype] == "paginated":
            scraper = IbExchangeListingMultipageReader()
        try:
            self.__website_contracts = scraper.read_ib_exchange_listing(
                self.__ctype,
                self.__exchange)
            self.__get_contracts_from_db()
            removed_count = self.__remove_deleted_contracts_from_db()
            added_count = self.__add_new_contracts_to_db()
        except ExitSignalDetectedError as e:
            self.__handle_exit_signal_detected_error(e)
        except WebscrapingReturnedNoResultError as e:
            self.__handle_query_returned_no_result_error(e)
        else:
            logger.info(
                f"Master listing synced for '{ctype}' on '{exchange}'. "
                f"{added_count} contracts were added, {removed_count} were "
                f"removed.")

    def __handle_exit_signal_detected_error(self, e):
        logger.info("Stopped.")

    def __handle_query_returned_no_result_error(self, e):
        logger.error(
            f"Webscraping for {self.__ctype} on {self.__exchange} returned "
            f"no results.")

    def __get_contracts_from_db(self) -> None:
        filters = {
            'contract_type_from_listing': self.__ctype,
            'exchange': self.__exchange}
        return_columns = ['broker_symbol', 'currency']
        self.__database_contracts = self.__contracts_db_connector.get_contracts(
            filters=filters,
            return_columns=return_columns)

    def __remove_deleted_contracts_from_db(self) -> int:
        contracts_removed = []  # todo remove
        removed_count = 0
        for db_row in self.__database_contracts:
            exists = False
            for web_row in self.__website_contracts:
                if ((db_row['broker_symbol'] == web_row['broker_symbol'])
                        and (db_row['currency'] == web_row['currency'])):
                    exists = True
                    break
            if not exists:
                self.__contracts_db_connector.delete_contract(
                    symbol=db_row['broker_symbol'],
                    exchange=self.__exchange.upper(),
                    currency=db_row['currency'])
                contracts_removed.append(
                    f"{self.__exchange.upper()}_{db_row['broker_symbol']}_"
                    f"{db_row['currency']}")
                removed_count += 1
        return removed_count

    def __add_new_contracts_to_db(self) -> int:
        contracts_added = []  # todo remove
        added_count = 0
        for web_row in self.__website_contracts:
            exists = False
            for db_row in self.__database_contracts:
                if ((web_row['broker_symbol'] == db_row['broker_symbol'])
                        and (web_row['currency'] == db_row['currency'])):
                    exists = True
                    break
            if not exists:
                self.__contracts_db_connector.create_contract(
                    contract_type_from_listing=self.__ctype,
                    exchange_symbol=web_row['exchange_symbol'],
                    broker_symbol=web_row['broker_symbol'],
                    name=web_row['name'],
                    currency=web_row['currency'],
                    exchange=self.__exchange.upper())
                contracts_added.append(
                    f"{self.__exchange.upper()}_{web_row['broker_symbol']}_"
                    f"{web_row['currency']}")
                added_count += 1
        return added_count
