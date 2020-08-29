import sqlite3
import os
import pandas as pd

from barbucket.database import DataBase


class QuotesDB(DataBase):

    def __init__(self):
        pass


    def insert_quotes(self, quotes):
        conn = self.connect()
        cur = conn.cursor()

        cur.executemany("""REPLACE INTO quotes (contract_id, date, open, high, 
            low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)""", quotes)

        conn.commit()
        cur.close()
        self.disconnect(conn)


    def get_quotes(self, contract_id):

        query = f"""SELECT date, open, high, low, close, volume
                    FROM quotes
                    WHERE contract_id = {contract_id}
                    ORDER BY date ASC;"""

        conn = self.connect()
        df = pd.read_sql_query(query, conn)
        self.disconnect(conn)

        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
            # more flexible to provide just strings
        df = df.set_index('date')

        return df


    def delete_quotes_before_date(self, contract_id, date):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(f"""DELETE FROM quotes
                        WHERE (contract_id = {contract_id}
                            AND date(date) <= '{date}')""")
        conn.commit()
        cur.close()
        self.disconnect(conn)


    def update_quotes_status(self, symbol, exchange, currency, status_code, 
        status_text):
        pass
        # status_text = self.remove_special_chars(status_text)
        
        # query = f"""UPDATE contracts 
        #             SET status_code = {status_code}, 
        #                 status_text = '{status_text}' 
        #             WHERE (broker_symbol = '{symbol}' 
        #                 AND exchange = '{exchange}'
        #                 AND currency = '{currency}');"""
        
        # conn = self.connect()
        # cur = conn.cursor()

        # cur.execute(query)

        # conn.commit()
        # cur.close()
        # self.disconnect(conn)