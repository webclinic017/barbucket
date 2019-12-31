import sqlite3
import os
import pandas as pd

from  data_management.database import DataBase
from  data_management.contracts_db import ContractsDB


class QuotesDB(DataBase):
    
    def __init__(self):
        pass


    def insert_quotes(self, contract_id, quotes):

        conn = self.connect()
        cur = conn.cursor()

        cur.executemany("""REPLACE INTO quotes (contract_id, date, open, high, 
            low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)""", quotes)

        conn.commit()
        cur.close()
        self.disconnect(conn)


    def clean_quotes_db_placeholder(self):
        # Check for quotes with no contracts
        # Check if data ends at date specified in contract
        # Check for data gaps
        pass


    def migrate_from_csv(self):
        # CSV_PATH = '/Users/martin/Google Drive/data/screener/'
        # cont_db = ContractsDB()

        # files = os.listdir(CSV_PATH)
        # for file in files[5000:5500]:
        #     print(file + ' ', end='')
        #     symbol = file.split('_')[0]
        #     exchange = file.split('_')[1].split('.')[0]
        #     contract = cont_db.get_contracts(ctype='ETF',
        #         symbol=symbol,
        #         exchange=exchange)
        #     if len(contract) == 0:
        #         print('not in contracts_db.')
        #         continue
        #     if len(contract) > 1:
        #         print(symbol+'_'+exchange+'_'+str(len(contract)))
        #         continue
        #     contract_id = contract[0]['contract_id']
        #     print('reading ', end='')
        #     df = pd.read_csv(CSV_PATH+file)
        #     print('converting ', end='')
        #     quotes = []
        #     for index, row in df.iterrows():
        #         quote = (
        #             contract_id,
        #             row['date'],
        #             row['open'],
        #             row['high'],
        #             row['low'],
        #             row['close'],
        #             row['volume']
        #         )
        #         quotes.append(quote)
        #     print('inserting ', end='')
        #     self.insert_quotes(contract_id=contract_id, quotes=quotes)
        #     print('done.')
        pass