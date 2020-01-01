import sqlite3
# import os
# from datetime import datetime
from tinydb import TinyDB, Query
from bs4 import BeautifulSoup
from selenium import webdriver

from data_management.database import DataBase


class ContractsDB(DataBase):

    def __init__(self):
        pass


    def create_contract(self, ctype, symbol, name, currency, exchange, 
        status_code=0, status_text='new contract'):
        # Todo: Return success or not

        status_text = self.remove_special_chars(status_text)

        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""INSERT INTO contracts (type, symbol, name, currency, 
            exchange, status_code, status_text) VALUES (?, ?, ?, 
            ?, ?, ?, ?)""", (ctype, symbol, name, currency, exchange, \
            status_code, status_text))

        conn.commit()
        cur.close()
        self.disconnect(conn)


    def get_contracts(self, ctype='*', symbol='*', name='*', currency='*', 
        exchange='*', status_code='*', status_text='*'):
        """
        returns a list of sqlite3.Row objects
        """

        query = 'SELECT * FROM contracts'

        filters = {}
        if ctype != '*': filters.update({'type': ctype})
        if symbol != '*': filters.update({'symbol': symbol})
        if name != '*': filters.update({'name': name})
        if currency != '*': filters.update({'currency': currency})
        if exchange != '*': filters.update({'exchange': exchange.upper()})
        if status_code != '*': filters.update({'status_code': status_code})
        if status_text != '*': filters.update({'status_text': status_text})

        if len(filters) > 0:
            query += ' WHERE '
        
        for key, value in filters.items():
            query += (key + " = '" + value + "' and ")

        if len(filters) > 0:
            query = query[:-5]

        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(query)
        result = cur.fetchall()

        conn.commit()
        cur.close()
        self.disconnect(conn)

        return result


    def update_contract_status(self, symbol, exchange, currency, status_code, 
        status_text):
        status_text = self.remove_special_chars(status_text)
        
        query = f"""UPDATE contracts 
                    SET status_code = {status_code}, 
                        status_text = '{status_text}' 
                    WHERE (symbol = '{symbol}' 
                        AND exchange = '{exchange}'
                        AND currency = '{currency}');"""
        
        conn = self.connect()
        cur = conn.cursor()

        cur.execute(query)

        conn.commit()
        cur.close()
        self.disconnect(conn)


    def delete_contract(self, symbol, exchange, currency):
        # Todo: Return number of deleted rows

        query = f"DELETE FROM contracts \
                    WHERE (symbol = '{symbol}' \
                        AND exchange = '{exchange}' \
                        AND currency = '{currency}');"
        
        conn = self.connect()
        cur = conn.cursor()

        cur.execute(query)

        conn.commit()
        cur.close()
        self.disconnect(conn)


    def delete_contract_id_placeholder(self, contract_id):
        # Todo: Return number of deleted rows

        # query = f"DELETE FROM contracts \
        #             WHERE contract_id = '{contract_id}';"
        
        # conn = self.connect()
        # cur = conn.cursor()

        # cur.execute(query)

        # conn.commit()
        # cur.close()
        # self.disconnect(conn)

        pass


    def delete_bad_status_contracts(self):
        query = 'DELETE FROM contracts \
                    WHERE (status_code = 162 \
                        OR status_code = 200 \
                        OR status_code = 354);'
        
        conn = self.connect()
        cur = conn.cursor()

        cur.execute(query)

        conn.commit()
        cur.close()
        self.disconnect(conn)


    def delete_bad_data_contracts_placeholder(self):
        pass


    def sync_contracts_to_listing(self, ctype, exchange):
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
                'type': ctype,
                'symbol': cols[0].text.strip(),
                'name': cols[1].text.strip(),
                'currency': cols[3].text.strip(),
                'exchange': exchange.upper()
            }
            website_data.append(row_dict)
        
        # Get contracts from database
        database_data = self.get_contracts(ctype=ctype, exchange=exchange)

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
                self.delete_contract(symbol=db_row['symbol'], \
                                    exchange=exchange.upper(),
                                    currency=db_row['currency'])
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
                    ctype=ctype,
                    symbol=web_row['symbol'],
                    name=web_row['name'],
                    currency=web_row['currency'],
                    exchange=exchange.upper(),
                )
                added_rows += 1
        print('added rows: ' + str(added_rows))


    def migrate_from_contracts_db(self):
        # Get contracts from old db
        # conn_old = sqlite3.connect('data_management/contracts.db')
        # conn_old.row_factory = sqlite3.Row
        # cur = conn_old.cursor()

        # query = 'SELECT * FROM contracts'
        # cur.execute(query)
        # old_contracts = cur.fetchall()

        # conn_old.commit()
        # cur.close()
        # conn_old.close()

        # # Create contracts in new db
        # for old_contract in old_contracts:
        #     self.create_contract(
        #         ctype='ETF', 
        #         symbol=old_contract['symbol'], 
        #         name=old_contract['name'], 
        #         currency=old_contract['currency'], 
        #         exchange=old_contract['exchange'], 
        #         status_code=old_contract['status'], 
        #         status_text=old_contract['status_text']
        #     )
        #     print('Created ' + old_contract['symbol'] + '_' + \
        #         old_contract['exchange'])
        pass