import sqlite3
from typing import Any

from .mediator import Mediator
from .custom_exceptions import QueryReturnedMultipleResultsError
from .custom_exceptions import QueryReturnedNoResultError


class QuotesStatusDbConnector():
    """Provides methods to access the 'quotes_status' table of the database."""

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator

    def get_quotes_status(self, contract_id: int) -> Any:
        """Get a contract's quote status from the db"""

        conn = self.mediator.notify("get_db_connection")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""SELECT *
                    FROM quotes_status
                    WHERE contract_id = ?;""", (contract_id,))
        result = cur.fetchall()
        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})

        if len(result) == 0:
            raise QueryReturnedNoResultError(f"Message")
        elif len(result) > 1:
            raise QueryReturnedMultipleResultsError(f"Message")
        else:
            return result[0]

    def insert_quotes_status(self, contract_id: int, status_code: int,
                             status_text: str,
                             daily_quotes_requested_from: str,
                             daily_quotes_requested_till: str) -> None:
        """ 
        Update a contract's quote status in the db.
        """

        # Status code:
        # 0: No quotes downloaded yet
        # 1: Successfully downloaded quotes
        # >1: TWS error code

        existing_status = self.get_quotes_status(contract_id=contract_id)

        if (status_code is None) and (existing_status is not None):
            status_code = existing_status['status_code']
        if (status_text is None) and (existing_status is not None):
            status_text = existing_status['status_text']
        if (daily_quotes_requested_from is None) and (existing_status is not None):
            daily_quotes_requested_from = existing_status['daily_quotes_requested_from']
        if (daily_quotes_requested_till is None) and (existing_status is not None):
            daily_quotes_requested_till = existing_status['daily_quotes_requested_till']

        conn = self.mediator.notify("get_db_connection")
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
        self.mediator.notify("close_db_connection", {'conn': conn})
