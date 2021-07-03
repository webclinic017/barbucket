import sqlite3
from pathlib import Path
from datetime import datetime
import logging

from barbucket.config import Config


class DatabaseConnector():
    config = Config()
    DB_PATH = Path.home() / config.get_config_value('database', 'db_location')

    def __init__(self):
        pass


    def connect(self):
        conn = sqlite3.connect(DatabaseConnector.DB_PATH)
        conn.execute("""
            PRAGMA foreign_keys = 1;
        """)
        return conn


    def disconnect(self, conn):
        conn.close()


    def _backup_database(self):
        # backup old database if exists
        if Path.is_file(DatabaseConnector.DB_PATH):
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            new_name = Path.home() / f".barbucket/database_backup_{timestamp}.db"
            DatabaseConnector.DB_PATH.rename(new_name)
            logging.info(f'Created backup of existing database: {new_name}')


    def _create_db_schema(self):
        # create new database and connect to
        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE contracts (
                contract_id INTEGER NOT NULL PRIMARY KEY,
                contract_type_from_listing TEXT,
                exchange_symbol TEXT, 
                broker_symbol TEXT, 
                name TEXT,
                currency TEXT, 
                exchange TEXT);""")

        cur.execute("""
            CREATE TABLE contract_details_ib (
                contract_id INTEGER UNIQUE,
                contract_type_from_details TEXT,
                primary_exchange TEXT,
                industry TEXT,
                category TEXT,
                subcategory TEXT,
                FOREIGN KEY (contract_id)
                    REFERENCES contracts (contract_id)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE,
                UNIQUE (contract_id));""")

        cur.execute("""
            CREATE TABLE contract_details_tv (
                contract_id INTEGER UNIQUE,
                market_cap INTEGER,
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
            CREATE VIEW all_contract_info AS
                SELECT * FROM contracts
                    LEFT JOIN contract_details_ib ON
                        contracts.contract_id = contract_details_ib.contract_id
                    LEFT JOIN contract_details_tv ON
                        contracts.contract_id = contract_details_tv.contract_id
                    LEFT JOIN quotes_status ON
                        contracts.contract_id = quotes_status.contract_id;""")

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
            CREATE TABLE quotes_status (
                contract_id INTEGER UNIQUE,
                status_code INTEGER,
                status_text TEXT,
                daily_quotes_requested_from TEXT,
                daily_quotes_requested_till TEXT,
                FOREIGN KEY (contract_id)
                    REFERENCES contracts (contract_id)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE,
                UNIQUE (contract_id));""")

        cur.execute("""
            CREATE TABLE universe_memberships (
                membership_id INTEGER NOT NULL PRIMARY KEY,
                contract_id INTEGER,
                universe TEXT,
                FOREIGN KEY (contract_id)
                    REFERENCES contracts (contract_id)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE);""")

        conn.commit()
        cur.close()
        db_connector.disconnect(conn)
        logging.info(f'Created new database.')


    def init_database(self,):
        self._backup_database()
        self._create_db_schema()

