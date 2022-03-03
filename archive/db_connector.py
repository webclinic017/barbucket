import sqlite3
from pathlib import Path
import logging

from .config_reader import ConfigReader

logger = logging.getLogger(__name__)


class DbConnector():
    """Handles all non-specific database operations."""
    __db_path: Path
    __is_initialized: bool = False

    def __init__(self) -> None:
        self.__config_reader = ConfigReader()
        if not DbConnector.__is_initialized:
            self.__initialize_database()
            DbConnector.__is_initialized = True

    def connect(self) -> sqlite3.Connection:
        """Provides a 'connection' object for the database.

        :raises DBNotInitializedError: The database needs to be initialized 
        by an internal method before use, this is handled automatically.
        :return: Connection object to the database
        :rtype: sqlite3.Connection
        """

        if not DbConnector.__db_path.is_file():
            raise DBNotInitializedError(
                f"Database file {DbConnector.__db_path} does not exist.")
            # otherwise sqlite3.connect() would create an empty file and
            # we dont want that
        conn = sqlite3.connect(DbConnector.__db_path)
        conn.execute("""
            PRAGMA foreign_keys = 1;
        """)
        # On SQLite, PRAGMA commands are only valid for the existing connection,
        # so this needs to be part of every db connection.
        return conn

    def disconnect(self, conn: sqlite3.Connection) -> None:
        """Disconnects the connection to the database.

        :param conn: Connection object, provided from this class
        :type conn: sqlite3.Connection
        """
        conn.close()

    def __initialize_database(self) -> None:
        """Initialize database if it doesnt exist. Else skip."""

        self.__get_db_path()
        if not DbConnector.__db_path.is_file():
            self.__create_db_file()
            self.__create_db_schema()
            logger.info("Database created. Finished db initialization.")
        else:
            logger.debug("Database already exists. Finished initialization.")

    def __get_db_path(self) -> None:
        db_path = self.__config_reader.get_config_value_single(
            section="database",
            option="db_location")
        DbConnector.__db_path = Path.home() / Path(db_path)

    def __create_db_file(self) -> None:
        conn = sqlite3.connect(DbConnector.__db_path)
        conn.close()
        logger.debug(f"Created new database file {DbConnector.__db_path}")

    def __create_db_schema(self) -> None:
        conn = self.connect()
        cur = conn.cursor()

        cur.execute(
            """CREATE TABLE contracts (
                    contract_id INTEGER NOT NULL PRIMARY KEY,
                    contract_type_from_listing TEXT,
                    exchange_symbol TEXT, 
                    broker_symbol TEXT, 
                    name TEXT,
                    currency TEXT, 
                    exchange TEXT);""")

        cur.execute(
            """CREATE TABLE contract_details_ib (
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

        cur.execute(
            """CREATE TABLE contract_details_tv (
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

        cur.execute(
            """CREATE VIEW all_contract_info AS
                    SELECT * FROM contracts
                        LEFT JOIN contract_details_ib ON
                            contracts.contract_id = contract_details_ib.contract_id
                        LEFT JOIN contract_details_tv ON
                            contracts.contract_id = contract_details_tv.contract_id
                        LEFT JOIN quotes_status ON
                            contracts.contract_id = quotes_status.contract_id;""")

        cur.execute(
            """CREATE TABLE quotes (
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

        cur.execute(
            """CREATE TABLE quotes_status (
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

        cur.execute(
            """CREATE TABLE universe_memberships (
                    membership_id INTEGER NOT NULL PRIMARY KEY,
                    contract_id INTEGER,
                    universe TEXT,
                    FOREIGN KEY (contract_id)
                        REFERENCES contracts (contract_id)
                            ON UPDATE CASCADE
                            ON DELETE CASCADE,
                    UNIQUE (contract_id, universe));""")

        conn.commit()
        cur.close()
        self.disconnect(conn)
        logger.debug("Created database schema.")


class DBNotInitializedError(Exception):
    """Custom exception for connecting to a non-present database."""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)
