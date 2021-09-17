import time
import logging
from typing import Any, Dict, List
import sqlite3
from abc import ABC

from bs4 import BeautifulSoup
import requests
import enlighten

from .mediator import Mediator
from .signal_handler import SignalHandler
from .custom_exceptions import ExitSignalDetectedError

logger = logging.getLogger(__name__)


class IbExchangeListingsProcessor():
    """Provides methods to sync local exchange listings to the IB website."""

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator
        self.__ctype: str = None
        self.__exchange: str = None
        self.__website_contracts: List[Any] = []
        self.__database_contracts: List[Any] = []

    def sync_contracts_to_listing(self, ctype: str, exchange: str) -> None:
        """Sync local exchange listings to the IB website"""

        self.__ctype = ctype
        self.__exchange = exchange

        # Get all contracts from website
        if ctype == "ETF":
            scraper = IbExchangeListingSinglepageReader()
        elif ctype == "STOCK":
            scraper = IbExchangeListingMultipageReader()
        try:
            self.__website_contracts = scraper.read_ib_exchange_listing(
                self.__ctype,
                self.__exchange)
        except ExitSignalDetectedError as e:
            self.mediator.notify(
                "show_cli_message",
                {'message': "Exiting on user request."})
            raise e

        self.__get_contracts_from_db()
        self.__remove_deleted_contracts_from_db()
        self.__add_new_contracts_to_db()

    def __get_contracts_from_db(self) -> None:
        filters = {
            'contract_type_from_listing': self.__ctype,
            'exchange': self.__exchange}
        columns = ['broker_symbol', 'currency']
        self.__database_contracts = self.mediator.notify(
            "get_contracts",
            {'filters': filters,
             'return_columns': columns})

    def __remove_deleted_contracts_from_db(self) -> None:
        contracts_removed = 0
        for db_row in self.__database_contracts:
            exists = False
            for web_row in self.__website_contracts:
                if ((db_row['broker_symbol'] == web_row['broker_symbol'])
                        and (db_row['currency'] == web_row['currency'])):
                    exists = True
                    break
            if not exists:
                self.mediator.notify(
                    "delete_contract",
                    {'symbol': db_row['broker_symbol'],
                     'exchange': self.__exchange.upper(),
                     'currency': db_row['currency']})
                contracts_removed += 1
        logger.debug(
            f"{contracts_removed} contracts removed from master listing.")
        # Todo: List Tickers and post to cli

    def __add_new_contracts_to_db(self) -> None:
        contracts_added = 0
        for web_row in self.__website_contracts:
            exists = False
            for db_row in self.__database_contracts:
                if ((web_row['broker_symbol'] == db_row['broker_symbol'])
                        and (web_row['currency'] == db_row['currency'])):
                    exists = True
                    break
            if not exists:
                self.mediator.notify(
                    "create_contract",
                    {'contract_type_from_listing': self.__ctype,
                     'exchange_symbol': web_row['exchange_symbol'],
                     'broker_symbol': web_row['broker_symbol'],
                     'name': web_row['name'],
                     'currency': web_row['currency'],
                     'exchange': self.__exchange.upper()})
                contracts_added += 1
        logger.debug(f"{contracts_added} contracts added to master listing.")
        # Todo: List Tickers and post to cli


class IbExchangeListingReader(ABC):
    def read_ib_exchange_listing(self):
        raise NotImplementedError


class IbExchangeListingSinglepageReader(IbExchangeListingReader):
    """Docstring"""

    def __init__(self) -> None:
        self.__html: str = None

    def read_ib_exchange_listing(self, ctype: str, exchange: str):
        """Docstring"""

        self.__get_html(exchange)
        self.__correct_ib_error()
        contracts = self.__extract_data(ctype, exchange)
        return contracts

    def __get_html(self, exchange: str) -> None:
        url = (
            f"https://www.interactivebrokers.com/en/index.php?f=567&exch="
            f"{exchange}")
        self.__html = requests.get(url).text

    def __correct_ib_error(self) -> None:
        old_lines = self.__html.splitlines()
        new_lines = []
        corrections = 0
        for line in old_lines:
            if (('        <td align="left" valign="middle">' in line)
                    and ("href" not in line)):
                line = line.replace("</a>", "")
                corrections += 1
            new_lines.append(line)
        self.__html = "".join(new_lines)
        if corrections == 0:
            logger.debug(
                f"IB error for singlepage listings no longer present. Checked "
                f"{len(old_lines)} lines.")

    def __extract_data(self, ctype: str, exchange: str) -> List[Dict[Any]]:
        soup = BeautifulSoup(self.__html, 'html.parser')
        tables = soup.find_all(
            'table',
            class_='table table-striped table-bordered')

        rows = tables[2].tbody.find_all('tr')
        website_contracts = []
        for row in rows:
            columns = row.find_all('td')
            row_dict = {
                'type': ctype,
                'broker_symbol': columns[0].text.strip(),
                'name': columns[1].text.strip(),
                'exchange_symbol': columns[2].text.strip(),
                'currency': columns[3].text.strip(),
                'exchange': exchange.upper()}
            website_contracts.append(row_dict)
        return website_contracts


class IbExchangeListingMultipageReader(IbExchangeListingReader):
    """Docstring"""

    def __init__(self) -> None:
        self.__signal_handler = SignalHandler()
        self.__current_page = 1
        self.__page_count = 1
        self.__html: str = None
        self.__website_data = []
        self.__ctype: str = None
        self.__exchange: str = None
        self.__manager = enlighten.get_manager()
        self.__pbar = self.__manager.counter(
            total=0,
            desc="Pages", unit="pages")

    def read_ib_exchange_listing(self, ctype: str, exchange: str):
        """Docstring"""

        self.__ctype: str = ctype
        self.__exchange: str = exchange

        while self.__current_page <= self.__page_count:
            self.__get_html()
            if self.__current_page == 1:
                self.__set_page_count()
            self.__correct_ib_error()
            self.__extract_data()
            logger.debug(
                f"Scraped IB exchange listing for {self.__exchange}, page "
                f"{self.__current_page}.")
            self.__check_abort_conditions()
            self.__pbar.update(incr=1)
            self.__current_page += 1
            if self.__current_page != self.__page_count:
                time.sleep(3)  # show some mercy to IB webserver
        return self.__website_data

    def __set_page_count(self) -> None:
        soup = BeautifulSoup(self.__html, 'html.parser')
        pagination_table = soup.find_all('ul', class_='pagination')
        page_buttons = pagination_table.find_all('li')
        self.__page_count = page_buttons[-2]
        self.__pbar.total = self.__page_count

    def __get_html(self) -> None:
        url = (f"https://www.interactivebrokers.com/en/index.php?f=2222"
               f"&exch={self.__exchange}&showcategories=STK&p=&cc=&limit="
               f"100&page={self.__current_page}")
        self.__html = requests.get(url).text

    def __correct_ib_error(self) -> None:
        if ("(click link for more details)</span></th>\n                       </th>"
                in self.__html):
            self.__html = self.__html.replace(
                "(click link for more details)</span></th>\n                       </th>\n",
                "(click link for more details)</span></th>\n")
        else:
            logger.debug(
                f"IB error for paginated listings no longer present. Checked "
                f"{len(self.__html.splitlines())} lines.")

    def __extract_data(self) -> List[Dict[Any]]:
        soup = BeautifulSoup(self.__html, 'html.parser')
        tables = soup.find_all(
            'table',
            class_='table table-striped table-bordered')
        rows = tables[2].tbody.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            row_dict = {
                'type': self.__ctype,
                'broker_symbol': cols[0].text.strip(),
                'name': cols[1].text.strip(),
                'exchange_symbol': cols[2].text.strip(),
                'currency': cols[3].text.strip(),
                'exchange': self.__exchange.upper()}
            self.__website_data.append(row_dict)

    def __check_abort_conditions(self) -> bool:
        """Check conditions to abort operation."""
        if self.__signal_handler.exit_requested():
            raise ExitSignalDetectedError
