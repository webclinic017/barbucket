import time
import logging
from typing import Dict, List
import sqlite3

from bs4 import BeautifulSoup
import requests

from .mediator import Mediator

logger = logging.getLogger(__name__)


class IbExchangeListingsProcessor():
    """Provides methods to sync local exchange listings to the IB website."""

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator
        self.__ctype = None
        self.__exchange = None

    def sync_contracts_to_listing(self, ctype: str, exchange: str) -> None:
        """Sync local exchange listings to the IB website"""

        self.__ctype = ctype
        self.__exchange = exchange

        # Get all contracts from websites
        if ctype == "ETF":
            website_data = self.__read_ib_exchange_listing_singlepage()
        elif ctype == "STOCK":
            website_data = self.__read_ib_exchange_listing_paginated()
        # Todo: SOLID

        # Abort, if webscraping was aborted by user
        if website_data == []:
            return
        # Todo: Exception

        database_data = self.__get_contracts_from_db(ctype, exchange)

        self.__remove_deleted_contracts_from_db(website_data, database_data)
        self.__add_new_contracts_to_db(website_data, database_data)

    def __read_ib_exchange_listing_singlepage(self):
        url = (f"https://www.interactivebrokers.com/en/index.php?f=567&exch="
               f"{self.__exchange}")
        html = requests.get(url).text

        # Correct error from IB
        old_lines = html.splitlines()
        new_lines = []
        corrections = 0
        for line in old_lines:
            if (
                ('        <td align="left" valign="middle">' in line)
                and
                ("href" not in line)
            ):
                line = line.replace("</a>", "")
                corrections += 1
            new_lines.append(line)
        html = "".join(new_lines)
        if corrections == 0:
            logger.info(f"IB error for singlepage listings no longer present"
                        f".")

        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all(
            'table',
            class_='table table-striped table-bordered')

        rows = tables[2].tbody.find_all('tr')
        website_data = []
        for row in rows:
            cols = row.find_all('td')
            row_dict = {
                'type': self.__ctype,
                'broker_symbol': cols[0].text.strip(),
                'name': cols[1].text.strip(),
                'exchange_symbol': cols[2].text.strip(),
                'currency': cols[3].text.strip(),
                'exchange': self.__exchange.upper()}
            website_data.append(row_dict)

        return website_data

    def __read_ib_exchange_listing_paginated(self):
        """
        Returns list of contracts
        Returns -1 if aborted by user
        """

        website_data = []
        page = 1

        # Setup progress bar
        # manager = enlighten.get_manager()
        # pbar = manager.counter(total=len(contracts), desc="Contracts", unit="contracts")

        while True:
            # Get website
            logger.info(f"Scraping IB exchange listing for {self.__exchange}"
                        f", page {page}.")
            url = (f"https://www.interactivebrokers.com/en/index.php?f=2222"
                   f"&exch={self.__exchange}&showcategories=STK&p=&cc=&limit="
                   f"100&page={page}")
            html = requests.get(url).text

            # Correct error from IB
            if "(click link for more details)</span></th>\n                       </th>" in html:
                html = html.replace(
                    "(click link for more details)</span></th>\n                       </th>\n",
                    "(click link for more details)</span></th>\n")
            else:
                logger.info(
                    f"IB error for paginated listings no longer present.")

            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            tables = soup.find_all(
                'table',
                class_='table table-striped table-bordered')
            rows = tables[2].tbody.find_all('tr')

            # Empty table -> End is reached
            if rows == []:
                return website_data

            # Add data from this page to 'website_data'
            for row in rows:
                cols = row.find_all('td')
                row_dict = {
                    'type': self.__ctype,
                    'broker_symbol': cols[0].text.strip(),
                    'name': cols[1].text.strip(),
                    'exchange_symbol': cols[2].text.strip(),
                    'currency': cols[3].text.strip(),
                    'exchange': self.__exchange.upper()}
                website_data.append(row_dict)

            # Check for Ctrl-C signal
            if self.mediator.notify("exit_signal"):
                logger.info(f"Exiting on user request.")
                return []

            # Prepare for next page
            page += 1
            time.sleep(3)  # show some mercy to IB webserver

    def __get_contracts_from_db(self, ctype: str, exchange: str
                                ) -> List[sqlite3.Row]:
        """Get all contracts from database"""

        filters = {'contract_type_from_listing': ctype, 'exchange': exchange}
        columns = ['broker_symbol', 'currency']
        database_data = self.mediator.notify(
            "get_contracts",
            {'filters': filters,
             'return_columns': columns})
        return database_data

    def __remove_deleted_contracts_from_db(self, website_data, database_data):
        """Delete contracts from database, that are not present in website"""

        contracts_removed = 0
        for db_row in database_data:
            exists = False
            for web_row in website_data:
                if (
                    (db_row['broker_symbol'] == web_row['broker_symbol'])
                    and
                    (db_row['currency'] == web_row['currency'])
                ):
                    exists = True
                    break
            if not exists:
                self.mediator.notify(
                    "delete_contract",
                    {'symbol': db_row['broker_symbol'],
                     'exchange': self.__exchange.upper(),
                     'currency': db_row['currency']})
                contracts_removed += 1
        logger.info(
            f"{contracts_removed} contracts removed from master listing.")

    def __add_new_contracts_to_db(self, website_data, database_data):
        """
        Add contracts from website to database, that are not present in 
        database
        """

        contracts_added = 0
        for web_row in website_data:
            exists = False
            for db_row in database_data:
                if (
                    (web_row['broker_symbol'] == db_row['broker_symbol'])
                    and
                    (web_row['currency'] == db_row['currency'])
                ):
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
        logger.info(f'{contracts_added} contracts added to master listing.')
