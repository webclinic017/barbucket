import sqlite3
import os
import pandas as pd

from data_management.database import DataBase


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


    def clean_quotes_db_placeholder(self):
        # Check for quotes with no contracts
        # Check if data ends at date specified in contract
        # Check for data gaps
        pass