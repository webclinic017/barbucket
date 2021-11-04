import logging
from typing import Any, List

from .contracts_db_connector import ContractsDbConnector
from .ib_exchange_listing_reader import (
    IbExchangeListingSinglepageReader,
    IbExchangeListingMultipageReader,
    WebscrapingReturnedNoResultError)
from .signal_handler import ExitSignalDetectedError


logger = logging.getLogger(__name__)


class IbExchangeListingsProcessor():
    """Provides methods to sync local exchange listings to the IB website."""

    def __init__(self) -> None:
        self.__contracts_db_connector = ContractsDbConnector()
        self.__ctype: str = ""
        self.__exchange: str = ""
        self.__website_contracts: List[Any] = []
        self.__database_contracts: List[Any] = []

    def sync_contracts_to_listing(self, ctype: str, exchange: str) -> None:
        """Sync local exchange listings to the IB website

        :param ctype: Contracts type to sync
        :type ctype: str
        :param exchange: Exchange to sync to
        :type exchange: str
        """

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
        except ExitSignalDetectedError:
            logger.info("Stopped.")
        except WebscrapingReturnedNoResultError:
            logger.error(f"Webscraping for {self.__ctype} on "
                         f"{self.__exchange} returned no results.")
        else:
            logger.info(
                f"Master listing synced for '{ctype}' on '{exchange}'. "
                f"{added_count} contracts were added, {removed_count} were "
                f"removed.")

    def __get_contracts_from_db(self) -> None:
        filters = {
            'contract_type_from_listing': self.__ctype,
            'exchange': self.__exchange}
        return_columns = ['broker_symbol', 'currency']
        self.__database_contracts = self.__contracts_db_connector.get_contracts(
            filters=filters,
            return_columns=return_columns)

    def __remove_deleted_contracts_from_db(self) -> int:
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
                    exchange=self.__exchange,
                    currency=db_row['currency'])
                removed_count += 1
        return removed_count

    def __add_new_contracts_to_db(self) -> int:
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
                    exchange=self.__exchange)
                added_count += 1
        return added_count
