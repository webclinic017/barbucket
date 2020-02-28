import sqlite3
import os
import pandas as pd

from  data_management.database import DataBase
from  data_management.contracts_db import ContractsDB


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
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(f"""SELECT date, open, high, low, close, volume
        FROM quotes WHERE contract_id = {contract_id}""")
        quotes = cur.fetchall()

        conn.commit()
        cur.close()
        self.disconnect(conn)

        return quotes


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