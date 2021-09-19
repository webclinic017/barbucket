import sqlite3
from typing import Any
import logging

from .mediator import Mediator
from .custom_exceptions import QueryReturnedMultipleResultsError
from .custom_exceptions import QueryReturnedNoResultError

logger = logging.getLogger(__name__)


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
            raise QueryReturnedNoResultError(f"Message")  # PROBLEM
        elif len(result) > 1:
            raise QueryReturnedMultipleResultsError(f"Message")
        else:
            return result[0]

    def insert_quotes_status(self, contract_id: int, status_code: int,
                             status_text: str,
                             daily_quotes_requested_from: str,
                             daily_quotes_requested_till: str) -> None:
        """ Update a contract's quote status in the db."""

        # Status code:
        # 0: No quotes downloaded yet
        # 1: Successfully downloaded quotes
        # >1: TWS error code

        existing_status = self.get_quotes_status(contract_id=contract_id)

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
        logger.debug(f"Inserted quotes status into db: {contract_id} "
                     f"{status_code} {status_text} "
                     f"{daily_quotes_requested_from} "
                     f"{daily_quotes_requested_till}")
