import sqlite3
import time
import logging

from bs4 import BeautifulSoup
import requests
import enlighten

from .mediator import Mediator


class ContractsDatabase():

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator

    def create_contract(self, contract_type_from_listing, exchange_symbol,
                        broker_symbol, name, currency, exchange):
        logging.debug(f"Creating new contract {contract_type_from_listing}_"
                      f"{exchange}_{broker_symbol}_{currency}.")
        conn = self.mediator.notify("get_db_connection", {})
        cur = conn.cursor()

        cur.execute(
            """INSERT INTO contracts (
                    contract_type_from_listing,
                    exchange_symbol,
                    broker_symbol,
                    name,
                    currency,
                    exchange)
                    VALUES (?, ?, ?, ?, ?, ?)""",
            (contract_type_from_listing,
                exchange_symbol,
                broker_symbol,
                name,
                currency,
                exchange))

        # Todo: insert_quotes_status as zero

        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})

    def get_contracts(self, filters={}, return_columns=[]):
        """returns a list of sqlite3.Row objects"""

        # Prepare query to get requested values from db
        query = "SELECT * FROM all_contract_info"

        if len(return_columns) > 0:
            cols = ", ".join(return_columns)
            query = query.replace("*", cols)

        if len(filters) > 0:
            query += " WHERE "

            for key, value in filters.items():
                if value == "NULL":
                    query += (key + " IS " + str(value) + " and ")
                elif isinstance(value, str):
                    query += (key + " = '" + str(value) + "' and ")
                elif isinstance(value, (int, float)):
                    query += (key + " = " + str(value) + " and ")

            query = query[:-5]  # remove trailing 'and'
            query += ";"

        # Get requested values from db
        logging.debug(f"Getting contracts from databse with query: {query}")
        conn = self.mediator.notify("get_db_connection", {})
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(query)
        contracts = cur.fetchall()

        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})

        return contracts

    def delete_contract(self, exchange, symbol, currency):
        conn = self.mediator.notify("get_db_connection", {})
        cur = conn.cursor()

        cur.execute(
            """DELETE FROM contracts
                    WHERE (broker_symbol = ?
                        AND exchange = ?
                        AND currency = ?);""",
            (symbol,
             exchange,
             currency))

        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})

    def delete_contract_id(self, contract_id):
        conn = self.mediator.notify("get_db_connection", {})
        cur = conn.cursor()

        cur.execute(
            """DELETE FROM contracts
                    WHERE contract_id = ?;""",
            contract_id)

        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})


class IbExchangeListings():

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator
        self.__ctype = None
        self.__exchange = None

    def sync_contracts_to_listing(self, ctype, exchange):
        logging.info(f"Syncing {ctype} contracts on {exchange} to master "
                     f"listing.")

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

        # Get all contracts from database
        filters = {'contract_type_from_listing': ctype, 'exchange': exchange}
        columns = ['broker_symbol', 'currency']
        database_data = self.mediator.notify(
            "get_contracts",
            {'filters': filters,
             'return_columns': columns})

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
            logging.info(
                f"IB error for singlepage listings no longer present.")

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
            logging.info(
                f"Scraping IB exchange listing for {self.__exchange}, page {page}.")
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
                logging.info(
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
                logging.info(f"Exiting on user request.")
                return []

            # Prepare for next page
            page += 1
            time.sleep(3)  # show some mercy to IB webserver

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
        logging.info(
            f"{contracts_removed} contracts removed from master listing.")

    def __add_new_contracts_to_db(self, website_data, database_data):
        """Add contracts from website to database, that are not present in database"""

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
        logging.info(f'{contracts_added} contracts added to master listing.')
