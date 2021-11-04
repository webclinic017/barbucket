import logging

from .db_connector import DbConnector

logger = logging.getLogger(__name__)


class TvDetailsDbConnector(DbConnector):
    """Provides methods to access the 'quotes' table of the database."""

    def __init__(self) -> None:
        super().__init__()

    def insert_tv_details(
            self, contract_id: int, market_cap: int, avg_vol_30_in_curr: int,
            country: str, employees: int, profit: int, revenue: int) -> None:
        """Writing tv details to db

        :param contract_id: Contract ID to insert details for
        :type contract_id: int
        :param market_cap: Market capitalization
        :type market_cap: int
        :param avg_vol_30_in_curr: Average trading volume of last 30 days in 
        contract's currency
        :type avg_vol_30_in_curr: int
        :param country: Country of origin
        :type country: str
        :param employees: Number of employees
        :type employees: int
        :param profit: Last annual profit
        :type profit: int
        :param revenue: Last annual revenue
        :type revenue: int
        """

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
        logger.debug(f"Wrote tv details for contract_id {contract_id} to db.")
