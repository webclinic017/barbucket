import sqlite3
import time
import logging

from bs4 import BeautifulSoup
import requests
import enlighten

from .database import DatabaseConnector
from .tools import GracefulExiter


class ContractsDatabase():

    def __init__(self):
        pass

    def create_contract(self, contract_type_from_listing, exchange_symbol,
                        broker_symbol, name, currency, exchange):
        logging.debug(
            f"Creating new contract {contract_type_from_listing}_{exchange}_{broker_symbol}_{currency}.")
        db_connector = DatabaseConnector()
        conn = db_connector.connect()
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

        conn.commit()
        cur.close()
        db_connector.disconnect(conn)

    def get_contracts(self, filters={}, return_columns=[]):
        """
        returns a list of sqlite3.Row objects
        """

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
        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(query)
        contracts = cur.fetchall()

        conn.commit()
        cur.close()
        db_connector.disconnect(conn)

        return contracts

    def delete_contract(self, exchange, symbol, currency):
        db_connector = DatabaseConnector()
        conn = db_connector.connect()
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
        db_connector.disconnect(conn)

    def delete_contract_id(self, contract_id):
        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        cur = conn.cursor()

        cur.execute(
            """DELETE FROM contracts 
                    WHERE contract_id = ?;""",
            contract_id)

        conn.commit()
        cur.close()
        db_connector.disconnect(conn)


class IbExchangeListings():

    def __init__(self):
        pass

    def read_ib_exchange_listing_singlepage(self, ctype, exchange):
        url = f"https://www.interactivebrokers.com/en/index.php?f=567"\
            + f"&exch={exchange}"
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
                'type': ctype,
                'broker_symbol': cols[0].text.strip(),
                'name': cols[1].text.strip(),
                'exchange_symbol': cols[2].text.strip(),
                'currency': cols[3].text.strip(),
                'exchange': exchange.upper()}
            website_data.append(row_dict)

        return website_data

    def read_ib_exchange_listing_paginated(self, ctype, exchange):
        """
        Returns list of contracts
        Returns -1 if aborted by user
        """

        website_data = []
        page = 1

        # Setup progress bar
        # manager = enlighten.get_manager()
        # pbar = manager.counter(total=len(contracts), desc="Contracts", unit="contracts")

        exiter = GracefulExiter()

        while True:
            # Get website
            logging.info(
                f"Scraping IB exchange listing for {exchange}, page {page}.")
            url = f"https://www.interactivebrokers.com/en/index.php?f=2222"\
                + f"&exch={exchange}&showcategories=STK&p=&cc=&limit=100"\
                + f"&page={page}"
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
                    'type': ctype,
                    'broker_symbol': cols[0].text.strip(),
                    'name': cols[1].text.strip(),
                    'exchange_symbol': cols[2].text.strip(),
                    'currency': cols[3].text.strip(),
                    'exchange': exchange.upper()}
                website_data.append(row_dict)

            # Check for abort signal
            if exiter.exit():
                logging.info(f"Exiting on user request.")
                return []

            # Prepare for next page
            page += 1
            time.sleep(3)  # show some mercy to webserver
