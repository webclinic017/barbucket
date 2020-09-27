import sqlite3
import time
from bs4 import BeautifulSoup
from numpy.core import numeric
import requests

from barbucket.database import DatabaseConnector


class ContractsDatabase():

    def __init__(self):
        pass


    def create_contract(self, contract_type_from_listing, exchange_symbol,
        broker_symbol, name, currency, exchange):
        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        cur = conn.cursor()

        cur.execute("""INSERT INTO contracts (
            contract_type_from_listing,
            exchange_symbol, 
            broker_symbol,
            name,
            currency,
            exchange) 
            VALUES (?, ?, ?, ?, ?, ?)""",(
            contract_type_from_listing,
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

        # Check if given filters and return-columns are valid
        # Query existing columns
        query = """SELECT name FROM PRAGMA_TABLE_INFO("all_contract_info");"""

        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(query)
        columns = cur.fetchall()

        conn.commit()
        cur.close()
        db_connector.disconnect(conn)

        existing_columns = []
        for column in columns:
            existing_columns.append(column['name'])

        # Check if given keys are in existing columns
        for key in filters:
            if key not in existing_columns:
                print(f"Error. Filter key '{key}' not found in columns.")
                return None

        # Check if given return_columns are in existing columns
        for column in return_columns:
            if column not in existing_columns:
                print(f"Error. Return-column key '{column}' not found in columns.")
                return None

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


            query = query[:-5]      #remove trailing 'and'
            query += ";"

        # Get requested values from db
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
        # Todo: Return number of deleted rows

        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        cur = conn.cursor()

        cur.execute("""DELETE FROM contracts
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
        # Todo: Return number of deleted rows

        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        cur = conn.cursor()

        cur.execute("""DELETE FROM contracts 
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

        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table', \
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
        website_data = []
        page = 1

        while True:
            # Get website
            print(str(page))
            url = f"https://www.interactivebrokers.com/en/index.php?f=2222"\
                + f"&exch={exchange}&showcategories=STK&p=&cc=&limit=100"\
                + f"&page={page}"
            html = requests.get(url).text

            # Correct error from IB
            if "(click link for more details)</span></th>\n                       </th>" in html:
                html = html.replace(\
                    "(click link for more details)</span></th>\n                       </th>\n",\
                    "(click link for more details)</span></th>\n")
                print("Error fixed.")

            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            tables = soup.find_all('table', \
                class_='table table-striped table-bordered')
            rows = tables[2].tbody.find_all('tr')

            # Empty table -> End is reached
            if rows == []:
                return website_data
            #################################################################
            if page == 3:
                return website_data
            #################################################################

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

            # Prepare for next page
            page += 1
            time.sleep(3) #show some mercy to webserver




