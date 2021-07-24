import sqlite3
from pathlib import Path
from datetime import datetime
import logging

from barbucket.config import Config


class DbNotInitializedError(Exception):
    """Custom exception for connecting to a non-present database."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)



class DatabaseConnector():
    """Handles all non-specific database operations."""

    __config = Config()
    _DB_PATH = Path.home() / __config.get_config_value_single('database', 'db_location')

    def __init__(self) -> None:
        pass


    def connect(self) -> sqlite3.Connection:
        """
        Provides a 'connection'-object for the database.
        Because in sqlite, PRAGMA orders need to be given to the connection object.
        """

        if not self._DB_PATH.is_file():
            raise DbNotInitializedError(message="Database does not exist. Call 'init_database()' before connecting.")
        # otherwise connect() would create an empty file

        conn = sqlite3.connect(self._DB_PATH)
        conn.execute("""
            PRAGMA foreign_keys = 1;
        """)
        return conn


    def disconnect(self, conn:sqlite3.Connection) -> None:
        """Disconnects the connection to the database."""

        conn.close()


    def archive_database(self) -> None:
        """Archive the database by renaming the file."""

        logging.info("Starting archivation of database.")
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S") # no colons in filenames
        new_name = self._DB_PATH.parent / f"database_archived_{timestamp}.db"
        try:
            self._DB_PATH.rename(new_name)
        except FileNotFoundError as e:
            logging.exception("Database not archived, because no databse exists.")
            raise FileNotFoundError from e
        else:
            logging.info(f"Database archived as: {new_name}")


    def _create_db_file(self) -> None:
        """Create a new database file."""

        conn = sqlite3.connect(self._DB_PATH)
        conn.close()
        logging.info("Created new database file.")


    def _create_db_schema(self) -> None:
        """Create schema in database."""

        logging.info("Started creating database schema.")
        conn = self.connect()
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
        self.disconnect(conn)
        logging.info("Finished creating database schema.")


    def init_database(self) -> None:
        """Initialize database if it doesnt exist. Else skip."""

        logging.info("Starting to initialize database.")
        if not self._DB_PATH.is_file():
            logging.info("Database does not exist. Starting to create it.")
            self._create_db_file()
            self._create_db_schema()
            logging.info("Database created. Finished initialization.")
        else:
            logging.info("Database already exists. Finished initialization.")


