import sqlite3
from pathlib import Path
from datetime import datetime

from barbucket.config import get_config_value


class DataBase():
    __DB_PATH = Path.home() / ".barbucket/database.db"


    def __init__(self):
        # If database file does not exist, initialize it
        if not Path.is_file(DataBase.__DB_PATH):
            self.init_database()


    def connect(self):
        conn = sqlite3.connect(DataBase.__DB_PATH)
        conn.execute("""
            PRAGMA foreign_keys = 1;
        """)
        return conn


    def disconnect(self, conn):
        conn.close()


    def init_database(self):
        # backup old database
        if Path.is_file(DataBase.__DB_PATH):
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H:%M:%S")
            new_name = Path.home() / f".barbucket/database_backup_{timestamp}.db"
            DataBase.__DB_PATH.rename(new_name)

        # create new database and connect to
        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE contracts (
                contract_id INTEGER NOT NULL PRIMARY KEY,
                contract_type_from_listing TEXT,
                contract_type_from_details TEXT,
                exchange_symbol TEXT, 
                broker_symbol TEXT, 
                name TEXT, 
                currency TEXT, 
                exchange TEXT, 
                primary_exchange TEXT,
                industry TEXT,
                category TEXT,
                subcategory TEXT);""")

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

        cur.execute("""
            CREATE TABLE universe_memberships (
                membership_id INTEGER NOT NULL PRIMARY KEY,
                contract_id INTEGER,
                universe TEXT);""")

        cur.execute("""
            CREATE TABLE contract_details_tw (
                contract_id INTEGER,
                market_cap TEXT,
                avg_vol_30_in_curr INTEGER,
                country TEXT,
                employees INTEGER,
                profit INTEGER,
                revenue INTEGER,
                FOREIGN KEY (contract_id)
                    REFERENCES contracts (contract_id)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE,
                UNIQUE (contract_id));""")

        cur.execute("""
            CREATE TABLE quotes_status (
                contract_id INTEGER,
                status_code INTEGER,
                status_text TEXT,
                daily_quotes_requested_from TEXT,
                daily_quotes_requested_till TEXT,
                FOREIGN KEY (contract_id)
                    REFERENCES contracts (contract_id)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE,
                UNIQUE (contract_id));""")

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
