import sqlite3
import time
from bs4 import BeautifulSoup
from selenium import webdriver

from barbucket.database import DataBase


class ContractsDB(DataBase):

    def __init__(self):
        self.__website_data = []


    def create_contract(self, ctype, exchange_symbol, broker_symbol, name,\
        currency, exchange, status_code=0, status_text='new contract'):
        # Todo: Return success or not

        status_text = self.remove_special_chars(status_text)

        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""INSERT INTO contracts (type, exchange_symbol,
            broker_symbol, name, currency, exchange, status_code, status_text) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (ctype, exchange_symbol, \
            broker_symbol, name, currency, exchange, status_code, status_text))

        conn.commit()
        cur.close()
        self.disconnect(conn)


    def get_contracts(self, contract_id='*', ctype='*', broker_symbol='*', \
        exchange_symbol='*', name='*', currency='*', exchange='*', \
        status_code='*', status_text='*'):
        """
        returns a list of sqlite3.Row objects
        """

        query = 'SELECT * FROM contracts'

        filters = {}
        if contract_id != '*': filters.update({'contract_id': contract_id})
        if ctype != '*': filters.update({'type': ctype})
        if broker_symbol != '*': filters.update({'broker_symbol': broker_symbol})
        if exchange_symbol != '*': filters.update({'exchange_symbol': exchange_symbol})
        if name != '*': filters.update({'name': name})
        if currency != '*': filters.update({'currency': currency})
        if exchange != '*': filters.update({'exchange': exchange.upper()})
        if status_code != '*': filters.update({'status_code': status_code})
        if status_text != '*': filters.update({'status_text': status_text})

        if len(filters) > 0:
            query += ' WHERE '
        
        for key, value in filters.items():
            query += (key + " = '" + str(value) + "' and ")

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
                    WHERE (broker_symbol = '{symbol}' 
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
                    WHERE (broker_symbol = '{symbol}' \
                        AND exchange = '{exchange}' \
                        AND currency = '{currency}');"
        
        conn = self.connect()
        cur = conn.cursor()

        cur.execute(query)

        conn.commit()
        cur.close()
        self.disconnect(conn)


    def delete_contract_id(self, contract_id):
        # Todo: Return number of deleted rows

        query = f"DELETE FROM contracts \
                    WHERE contract_id = '{contract_id}';"
        
        conn = self.connect()
        cur = conn.cursor()

        cur.execute(query)

        conn.commit()
        cur.close()
        self.disconnect(conn)


    def __read_ib_listing_singlepage(self, ctype, exchange):
        url = f"https://www.interactivebrokers.com/en/index.php?f=567"\
            + f"&exch={exchange}"
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        browser = webdriver.Chrome(chrome_options=options)
        browser.get(url)
        html = browser.page_source
        browser.quit()

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


    def __read_ib_listing_paginated(self, ctype, exchange):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        browser = webdriver.Chrome(chrome_options=options)
        website_data = []
        page = 1

        while True:
            print(str(page))
            url = f"https://www.interactivebrokers.com/en/index.php?f=2222"\
                + f"&exch={exchange}&showcategories=STK&p=&cc=&limit=100"\
                + f"&page={page}"
            browser.get(url)
            html = browser.page_source
            soup = BeautifulSoup(html, 'html.parser')
            tables = soup.find_all('table', \
                class_='table table-striped table-bordered')

            # Empty table -> End is reached
            rows = tables[2].tbody.find_all('tr')
            if rows == []:
                browser.quit()
                return website_data

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

            page += 1
            time.sleep(3) #show some mercy to webserver


    def sync_contracts_to_listing(self, ctype, exchange):
        # Todo: Return statistics

        # Get contracts from websites
        print(f'exchange: {exchange}')
        if ctype.lower() == "etf":
            self.__website_data = self.__read_ib_listing_singlepage(ctype, exchange)
        elif ctype.lower() == "stock":
            self.__website_data = self.__read_ib_listing_paginated(ctype, exchange)

        # Get contracts from database for deleting
        database_data = self.get_contracts(ctype=ctype, exchange=exchange)

        # Delete contracts from database, that are not present in website
        deleted_rows = 0
        for db_row in database_data:
            exists = False
            for web_row in self.__website_data:
                if db_row['broker_symbol'] == web_row['broker_symbol']:
                    exists = True
                    break
            if not exists:
                print('deleting: ' + db_row['broker_symbol'] + ' - ' + exchange.upper())
                self.delete_contract(
                    symbol=db_row['broker_symbol'], \
                    exchange=exchange.upper(),
                    currency=db_row['currency'])
                deleted_rows += 1
        print('deleted rows: ' + str(deleted_rows))

        # Add contracts from website to database, that are not present in database
        added_rows = 0
        for web_row in self.__website_data:
            exists = False
            for db_row in database_data:
                if web_row['broker_symbol'] == db_row['broker_symbol']:
                    exists = True
                    break
            if not exists:
                print('creating: ' + web_row['broker_symbol'] + ' - ' + exchange.upper())
                self.create_contract(
                    ctype=ctype,
                    exchange_symbol=web_row['exchange_symbol'],
                    broker_symbol=web_row['broker_symbol'],
                    name=web_row['name'],
                    currency=web_row['currency'],
                    exchange=exchange.upper(),)
                added_rows += 1
        print('added rows: ' + str(added_rows))

        # Clean up
        self.__website_data = []