import sqlite3
from typing import Any
import logging

from .db_connector import DbConnector

logger = logging.getLogger(__name__)


class QuotesStatusDbConnector(DbConnector):
    """Provides methods to access the 'quotes_status' table of the database.

    Status code:
    0: No quotes downloaded yet
    1: Successfully downloaded quotes
    >1: TWS error code
    """

    def __init__(self) -> None:
        super().__init__()

    def get_quotes_status(self, contract_id: int) -> Any:
        """Get a contract's quote status from the db. Create, if entry does not 
        exist.

        :param contract_id: Contract ID to provide the quotes download status 
        for
        :type contract_id: int
        :return: Current quotes download status from the database for the 
        given contract
        :rtype: Any
        """

        if not self.__check_status_exists(contract_id=contract_id):
            self.__create_status_entry(contract_id=contract_id)
        return self.__get_status(contract_id=contract_id)

    def __check_status_exists(self, contract_id: int) -> Any:
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """SELECT COUNT(*) FROM quotes_status WHERE contract_id = ?;""",
            (contract_id,))
        count = cur.fetchone()
        conn.commit()
        cur.close()
        self.disconnect(conn)
        if count[0] > 0:
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
                    (contract_id,))
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
        """Update a contract's quote status in the db.

        :param contract_id: Contract ID to update the quotes download status 
        for
        :type contract_id: int
        :param status_code: Status code from TWS
        :type status_code: int
        :param status_text: Status text, from TWS if error
        :type status_text: str
        :param daily_quotes_requested_from: Earlist date that quotes were 
        requested for
        :type daily_quotes_requested_from: str
        :param daily_quotes_requested_till: Latest date that quotes were 
        requested for
        :type daily_quotes_requested_till: str
        """

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
        logger.debug(f"Inserted quotes status into db: '{contract_id}', "
                     f"'{status_code}', '{status_text}', "
                     f"'{daily_quotes_requested_from}', "
                     f"'{daily_quotes_requested_till}'")
