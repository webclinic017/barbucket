import sqlite3
from pathlib import Path

from .mediator import Mediator
from .custom_exceptions import DbNotInitializedError


class DbConnector():
    """Handles all non-specific database operations."""

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator
        self._DB_PATH = None

    def connect(self) -> sqlite3.Connection:
        """Provides a 'connection'-object for the database."""

        self.__get_db_path()
        if not self._DB_PATH.is_file():
            raise DbNotInitializedError("Database does not exist. Call "
                                        "'init_database()' before connecting.")
            # otherwise connect() would create an empty file
        conn = sqlite3.connect(self._DB_PATH)
        conn.execute("""
            PRAGMA foreign_keys = 1;
        """)
        # On SQLite, PRAGMA commands are only valid for the existing connection,
        # so this needs to be part of every db connection.
        return conn

    def disconnect(self, conn: sqlite3.Connection) -> None:
        """Disconnects the connection to the database."""
        conn.close()

    def __get_db_path(self) -> None:
        conf_path = self.mediator.notify(
            "get_config_value_single",
            {'section': "database", 'option': "db_location"})
        self._DB_PATH = Path.home() / Path(conf_path)
