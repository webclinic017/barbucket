import sqlite3
import os
from datetime import datetime



class DataBase():
    DB_PATH = 'data_management/database.db'

    def __init__(self):
        pass


    def init_database(self):
        # backup old database
        if os.path.isfile(self.DB_PATH):
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H:%M:%S")
            new_name = self.DB_PATH.split('.')[0] + '_backup_' + timestamp + '.db'
            os.rename(self.DB_PATH, new_name)

        # create new database
        conn = sqlite3.connect(self.DB_PATH)
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE contracts (
                contract_id INTEGER NOT NULL PRIMARY KEY,
                type TEXT,
                symbol TEXT, 
                name TEXT, 
                currency TEXT, 
                exchange TEXT, 
                status_code INTEGER,
                status_text TEXT)
        ''')

        cur.execute('''
            CREATE TABLE quotes (
                contract_id INTEGER,
                date TEXT,
                open REAL,
                high REAL, 
                low REAL, 
                close REAL,
                volume REAL,
                FOREIGN KEY (contract_id)
                    REFERENCES contracts (contract_id)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE,
                UNIQUE (contract_id, date))
        ''')

        conn.commit()
        cur.close()
        conn.close()


    @staticmethod
    def remove_special_chars(input_string):
        special_chars = ["'"]
        result = input_string
        for char in special_chars:
            result = result.replace(char, '')
        return result
