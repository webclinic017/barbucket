import sqlite3
from pathlib import Path
from datetime import datetime
import logging

from .mediator import Mediator

logger = logging.getLogger(__name__)


class DbInitializer():
    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator
        self._DB_PATH = None

    def initialize_database(self) -> None:
        """Initialize database if it doesnt exist. Else skip."""

        self.__get_db_path()
        if not self._DB_PATH.is_file():
            self._create_db_file()
            self._create_db_schema()
            logger.debug("Database created. Finished initialization.")
        else:
            logger.debug("Database already exists. Finished initialization.")

    def __get_db_path(self) -> None:
        conf_path = self.mediator.notify(
            "get_config_value_single",
            {'section': "database", 'option': "db_location"})
        self._DB_PATH = Path.home() / Path(conf_path)

    def _create_db_file(self) -> None:
        """Create a new database file."""

        conn = sqlite3.connect(self._DB_PATH)
        conn.close()
        logger.debug("Created new database file.")

    def _create_db_schema(self) -> None:
        """Create schema in database."""

        logger.debug("Started creating database schema.")
        conn = self.mediator.notify("get_db_connection", {})
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
        self.mediator.notify("close_db_connection", {'conn': conn})
        logger.debug("Finished creating database schema.")

    def archive_database(self) -> None:
        """Archive the database by renaming the file."""

        self.__get_db_path()
        now = datetime.now()
        timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")  # no colons in filenames
        new_name = self._DB_PATH.parent / f"database_archived_{timestamp}.db"
        try:
            self._DB_PATH.rename(new_name)
        except FileNotFoundError as e:
            logger.warn("Database not archived, because no databse "
                        "exists.")
            raise FileNotFoundError from e
        else:
            logger.debug(f"Database archived as: {new_name}")
