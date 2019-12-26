import sqlite3
import os
from datetime import datetime
from tinydb import TinyDB, Query
from bs4 import BeautifulSoup
from selenium import webdriver


class ContractsDB:
    __DB_PATH = 'data_management/contracts.db'


    def __init__(self):
        pass


    def connect_placeholder(self):
        pass


    def disconnect_placeholder(self):
        pass


    def init_database(self):
        # backup old database
        if os.path.isfile(self.__DB_PATH):
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H:%M:%S")
            new_name = self.__DB_PATH.split('.')[0] + '_backup_' + timestamp + '.db'
            os.rename(self.__DB_PATH, new_name)

        # create new database
        conn = sqlite3.connect(self.__DB_PATH)
        cur = conn.cursor()

        cur.execute('''CREATE TABLE contracts (
            symbol text, 
            name text, 
            currency text, 
            exchange text, 
            status integer,
            status_text text)''')

        conn.commit()
        cur.close()
        conn.close()


    def create_contract(self, symbol, name, currency, exchange, status=0, \
        status_text='new contract'):
        # Todo: Return success or not

        conn = sqlite3.connect(self.__DB_PATH)
        cur = conn.cursor()

        cur.execute("""INSERT INTO contracts VALUES (?, ?, ?,
            ?, ?, ?)""", (symbol, name, currency, exchange, status, status_text))

        conn.commit()
        cur.close()
        conn.close()


    def get_contracts(self, symbol='*', name='*', currency='*', exchange='*', \
        status='*', status_text='*'):
        """
        returns a list of sqlite3.Row objects
        """

        query = 'SELECT * FROM contracts'

        filters = {}
        if symbol != '*': filters.update({'symbol': symbol})
        if name != '*': filters.update({'name': name})
        if currency != '*': filters.update({'currency': currency})
        if exchange != '*': filters.update({'exchange': exchange.upper()})
        if status != '*': filters.update({'status': status})
        if status_text != '*': filters.update({'status_text': status_text})

        if len(filters) > 0:
            query += ' WHERE '
        
        for key, value in filters.items():
            query += (key + " = '" + value + "' and ")

        if len(filters) > 0:
            query = query[:-5]

        conn = sqlite3.connect(self.__DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(query)
        result = cur.fetchall()

        conn.commit()
        cur.close()
        conn.close()

        return result


    def update_contract_status(self, symbol, exchange, status, status_text):
        status_text = status_text.replace("'", "")
        
        query = f"UPDATE contracts \
                    SET status = {status}, status_text = '{status_text}' \
                    WHERE (symbol = '{symbol}' AND exchange = '{exchange}')"
        
        conn = sqlite3.connect(self.__DB_PATH)
        cur = conn.cursor()

        cur.execute(query)

        conn.commit()
        cur.close()
        conn.close()


    def delete_contract(self, symbol, exchange):
        # Todo: Return number of deleted rows

        query = f"DELETE FROM contracts WHERE (symbol = '{symbol}' AND exchange = '{exchange}')"
        
        conn = sqlite3.connect(self.__DB_PATH)
        cur = conn.cursor()

        cur.execute(query)

        conn.commit()
        cur.close()
        conn.close()


    def import_from_tinydb(self):
        # TINY_DB_PATH = 'data_management/contracts_db.json'
        
        # self.init_database()

        # tiny_contracts_db = TinyDB(TINY_DB_PATH)
        # result = tiny_contracts_db.all()
        # tiny_contracts_db.close()

        # for contract in result:
        #     status = -1
        #     if contract['Status'].startswith('Error:200_'):
        #         status = 200
        #     elif contract['Status'].startswith('Error:162_'):
        #         status = 162
        #     elif contract['Status'].startswith('data_ends:'):
        #         status = 1
        #     elif contract['Status'].startswith('no_data'):
        #         status = 0

        #     self.create_contract(
        #         symbol=contract['Symbol'],
        #         name=contract['Name'],
        #         currency=contract['Currency'],
        #         exchange=contract['Exchange'],
        #         status=status,
        #         status_text=contract['Status'])
        pass


    def delete_no_data_contracts(self):
        query = 'DELETE FROM contracts WHERE (status = 162 OR status = 200)'
        
        conn = sqlite3.connect(self.__DB_PATH)
        cur = conn.cursor()

        cur.execute(query)

        conn.commit()
        cur.close()
        conn.close()


    def delete_bad_data_contracts_placeholder(self):
        pass


    def sync_contracts_to_listing(self, exchange):
        # Todo: Return statistics

        # Get contracts from website
        print(f'exchange: {exchange}')
        url = f'https://www.interactivebrokers.com/en/index.php?f=567&exch={exchange}'
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        browser = webdriver.Chrome(chrome_options=options)
        browser.get(url)
        html = browser.page_source
        browser.quit()

        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table', class_='table table-striped table-bordered')

        website_data = []
        rows = tables[2].tbody.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            row_dict = {
                'symbol': cols[0].text.strip(),
                'name': cols[1].text.strip(),
                'currency': cols[3].text.strip(),
                'exchange': exchange.upper()
            }
            website_data.append(row_dict)
        
        # Get contracts from database
        database_data = self.get_contracts(exchange=exchange)

        # Delete contracts from database, that are not present in website
        deleted_rows = 0
        for db_row in database_data:
            exists = False
            for web_row in website_data:
                if db_row['symbol'] == web_row['symbol']:
                    if db_row['currency'] == web_row['currency']:
                        exists = True
                        break
            if not exists:
                print('deleting: ' + db_row['symbol'] + ' - ' + exchange.upper())
                self.delete_contract(symbol=db_row['symbol'], exchange=exchange.upper())
                deleted_rows += 1
        print('deleted rows: ' + str(deleted_rows))

        # Add contracts from website to database, that are not present in database
        added_rows = 0
        for web_row in website_data:
            exists = False
            for db_row in database_data:
                if web_row['symbol'] == db_row['symbol']:
                    if web_row['currency'] == db_row['currency']:
                        exists = True
                        break
            if not exists:
                print('creating: ' + web_row['symbol'] + ' - ' + exchange.upper())
                self.create_contract(
                    symbol=web_row['symbol'],
                    name=web_row['name'],
                    currency=web_row['currency'],
                    exchange=exchange.upper(),
                )
                added_rows += 1
        print('added rows: ' + str(added_rows))


    def remove_old_contracts_from_web_placeholder(self):
        pass


