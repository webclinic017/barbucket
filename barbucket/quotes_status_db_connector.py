import sqlite3
from typing import Any
import logging

from .db_connector import DbConnector

logger = logging.getLogger(__name__)


class QuotesStatusDbConnector(DbConnector):
    """Provides methods to access the 'quotes_status' table of the database."""

    def __init__(self) -> None:
        super().__init__()

    def get_quotes_status(self, contract_id: int) -> Any:
        """
        Get a contract's quote status from the db. Create, if entry does not 
        exist.
        """

        if self.__check_status_exists(contract_id=contract_id):
            status_entry = self.__get_status(contract_id=contract_id)
        else:
            self.__create_status_entry(contract_id=contract_id)
            status_entry = self.__get_status(contract_id=contract_id)
        return status_entry

    def __check_status_exists(self, contract_id: int) -> Any:
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """SELECT COUNT(* WHERE contract_id = ?);""",
            (contract_id,))
        count = cur.fetchone()
        conn.commit()
        cur.close()
        self.disconnect(conn)
        if count > 0:
            return True
        else:
            return False

    def __get_status(self, contract_id: int) -> Any:
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""SELECT *
                    FROM quotes_status
                    WHERE contract_id = ?;""",
                    (contract_id))
        result = cur.fetchone()
        conn.commit()
        cur.close()
        self.disconnect(conn)
        return result

    def __create_status_entry(self, contract_id: int) -> None:
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            """REPLACE into quotes_status(
                contract_id,
                status_code,
                status_text,
                daily_quotes_requested_from,
                daily_quotes_requested_till) VALUES(?, ?, ?, ?, ?)""",
            (contract_id,
                0,
                "No quotes downloaded yet.",
                "NULL",
                "NULL"))
        conn.commit()
        cur.close()
        self.disconnect(conn)
        logger.debug(f"Created new quotes_status_db entry: {contract_id}.")

    def update_quotes_status(self, contract_id: int, status_code: int,
                             status_text: str,
                             daily_quotes_requested_from: str,
                             daily_quotes_requested_till: str) -> None:
        """ Update a contract's quote status in the db."""

        # Status code:
        # 0: No quotes downloaded yet
        # 1: Successfully downloaded quotes
        # >1: TWS error code

        if ((daily_quotes_requested_from == None)
                or (daily_quotes_requested_till == None)):  # Db entry might not exist yet.
            existing_status = self.get_quotes_status(contract_id=contract_id)
            if ((daily_quotes_requested_from is None)
                    and (existing_status is not None)):
                daily_quotes_requested_from = existing_status[
                    'daily_quotes_requested_from']
            if ((daily_quotes_requested_till is None)
                    and (existing_status is not None)):
                daily_quotes_requested_till = existing_status[
                    'daily_quotes_requested_till']

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            """REPLACE into quotes_status(
                contract_id,
                status_code,
                status_text,
                daily_quotes_requested_from,
                daily_quotes_requested_till) VALUES(?, ?, ?, ?, ?)""",
            (contract_id,
             status_code,
             status_text,
             daily_quotes_requested_from,
             daily_quotes_requested_till))
        conn.commit()
        cur.close()
        self.disconnect(conn)
        logger.debug(f"Inserted quotes status into db: {contract_id} "
                     f"{status_code} {status_text} "
                     f"{daily_quotes_requested_from} "
                     f"{daily_quotes_requested_till}")
