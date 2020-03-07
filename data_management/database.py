import sqlite3
import os
from datetime import datetime
import configparser


class DataBase():
    config = configparser.ConfigParser()
    config.read('data_management/config.ini')
    __DB_PATH = config.get('database', 'db_path')

    def __init__(self):
        # If database file does not exist, initialize it
        if not os.path.isfile(self.__DB_PATH):
            self.init_database()


    def connect(self):
        conn = sqlite3.connect(self.__DB_PATH)
        conn.execute("""
            PRAGMA foreign_keys = 1;
        """)
        return conn


    def disconnect(self, conn):
        conn.close()


    def init_database(self):
        # backup old database
        if os.path.isfile(self.__DB_PATH):
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H:%M:%S")
            new_name = self.__DB_PATH.split('.')[0] + '_backup_' + timestamp + '.db'
            os.rename(self.__DB_PATH, new_name)

        # create new database and connect to
        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE contracts (
                contract_id INTEGER NOT NULL PRIMARY KEY,
                type TEXT,
                symbol TEXT, 
                name TEXT, 
                currency TEXT, 
                exchange TEXT, 
                status_code INTEGER,
                status_text TEXT);""")
        cur.execute("""
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
                UNIQUE (contract_id, date));""")

        conn.commit()
        cur.close()
        self.disconnect(conn)


    @staticmethod
    def remove_special_chars(input_string):
        special_chars = ["'"]
        result = input_string
        for char in special_chars:
            result = result.replace(char, '')
        return result
