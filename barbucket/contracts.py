import sqlite3
import time
from bs4 import BeautifulSoup
import requests

from barbucket.database import DatabaseConnector
from barbucket.tws import Tws


class ContractsDatabase():

    def __init__(self):
        pass


    def get_contracts(self, filters={}, return_columns=[]):
        """
        returns a list of sqlite3.Row objects
        """

        # Check if given filters and return-columns are valid
        # Query existing columns
        query = """SELECT name FROM PRAGMA_TABLE_INFO("contracts");"""

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
        query = 'SELECT * FROM contracts'

        if len(return_columns) > 0:
            cols = ", ".join(return_columns)
            query = query.replace("*", cols)

        if len(filters) > 0:
            query += ' WHERE '

            for key, value in filters.items():
                query += (key + " = '" + str(value) + "' and ")

            query = query[:-5]      #remove trailing 'and'

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


    def delete_contract(self, contraxt_type, exchange, symbol, currency):
        # Todo: Return number of deleted rows

        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        cur = conn.cursor()

        cur.execute("""DELETE FROM contracts
                        WHERE (broker_symbol = ? 
                            AND exchange = ? 
                            AND currency = ?);""",
                            symbol,
                            exchange,
                            currency)

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



class Contracts():

    def create_contract(self, contract_type_from_listing, broker_symbol, exchange, currency):
        # Todo: Return success or not

        # Check if identical contract is already present
        contracts_database = ContractsDatabase()
        filters = {'exchange': exchange,
            'contract_type_from_listing': contract_type_from_listing,
            'broker_symbol': broker_symbol,
            'currency': currency}
        columns = ['contract_id']
        existing = contracts_database.get_contracts(filters=filters,
            return_columns=columns)
        if len(existing) > 0:
            print("Error. Contract already existing.")
            return

        # Get IB contract details from TWS
        tws = Tws()
        tws.connect()
        details = tws.get_contract_details(
            contract_type_from_listing=contract_type_from_listing,
            broker_symbol=broker_symbol,
            exchange=exchange,
            currency=currency)
        tws.disconnect()

        if details == None:
            print("Error. No details returned from TWS. Aborting contract.")
            return
        
        # Store combined values into db
        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        cur = conn.cursor()

        cur.execute("""INSERT INTO contracts (
            contract_type_from_listing,
            contract_type_from_details,
            exchange_symbol, 
            broker_symbol,
            name,
            currency,
            exchange,
            primary_exchange,
            industry,
            category,
            subcategory) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",(
            contract_type_from_listing,
            details.stockType,
            details.contract.localSymbol,
            broker_symbol,
            details.longName,
            currency,
            details.contract.exchange,
            details.contract.primaryExchange,
            details.industry,
            details.category,
            details.subcategory))

        conn.commit()
        cur.close()
        db_connector.disconnect(conn)


    def sync_contracts_to_listing(self, ctype, exchange):
        # Todo: Return statistics

        # Get all contracts from websites
        print(f'exchange: {exchange}')
        ib_listings = IbExchangeListings()
        website_data = []
        if ctype == "ETF":
            website_data = ib_listings.read_ib_exchange_listing_singlepage(ctype, exchange)
        elif ctype == "STOCK":
            website_data = ib_listings.read_ib_exchange_listing_paginated(ctype, exchange)

        # Get all contracts from database
        contracts_database = ContractsDatabase()
        filters = {'contract_type_from_listing': ctype, 'exchange': exchange}
        columns = ['broker_symbol', 'currency']
        database_data = contracts_database.get_contracts(filters=filters,
            return_columns=columns)

        # Delete contracts from database, that are not present in website
        contracts_removed = 0
        for db_row in database_data:
            exists = False
            for web_row in website_data:
                if (db_row['broker_symbol'] == web_row['broker_symbol']) and \
                    (db_row['currency'] == web_row['currency']):
                    exists = True
                    break
            if not exists:
                print('deleting: ' + db_row['broker_symbol'] + ' - ' + exchange)
                contracts_database.delete_contract(
                    symbol=db_row['broker_symbol'], \
                    exchange=exchange.upper(),
                    currency=db_row['currency'])
                contracts_removed += 1
        print('contracts removed: ' + str(contracts_removed))

        # Add contracts from website to database, that are not present in database
        contracts_added = 0
        for web_row in website_data:
            exists = False
            for db_row in database_data:
                if (web_row['broker_symbol'] == db_row['broker_symbol']) and\
                    (web_row['currency'] == db_row['currency']):
                    exists = True
                    break
            if not exists:
                print('creating: ' + web_row['broker_symbol'] + ' - ' + exchange)
                contracts_database.create_contract(
                    contract_type_from_listing=ctype,
                    broker_symbol=web_row['broker_symbol'],
                    exchange=exchange.upper(),
                    currency=web_row['currency'])
                contracts_added += 1
        print('contracts added: ' + str(contracts_added))
