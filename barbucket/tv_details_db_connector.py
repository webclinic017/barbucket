import logging

from .mediator import Mediator
from .db_connector import DbConnector

logger = logging.getLogger(__name__)


class TvDetailsDbConnector(DbConnector):
    """Provides methods to access the 'quotes' table of the database."""

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator

    def insert_tv_details(
            self, contract_id: int, market_cap: int, avg_vol_30_in_curr: int,
            country: str, employees: int, profit: int, revenue: int) -> None:
        """Writing tv details to db"""

        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""
            REPLACE INTO contract_details_tv (
                contract_id,
                market_cap,
                avg_vol_30_in_curr,
                country,
                employees,
                profit,
                revenue)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
            contract_id,
            market_cap,
            avg_vol_30_in_curr,
            country,
            employees,
            profit,
            revenue))
        conn.commit()
        cur.close()
        self.disconnect(conn)
        logger.debug("Wrote tv details for contract_id {contract_id} to db.")
