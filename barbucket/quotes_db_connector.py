from typing import List, Any
import logging

import pandas as pd

from .db_connector import DbConnector

logger = logging.getLogger(__name__)


class QuotesDbConnector(DbConnector):
    """Provides methods to access the 'quotes' table of the database."""

    def __init__(self) -> None:
        super().__init__()

    def insert_quotes(self, quotes: List[Any]) -> None:
        """Insert quotes into the db

        :param quotes: quotes
        :type quotes: List[Any]
        """

        conn = self.connect()
        cur = conn.cursor()
        cur.executemany("""REPLACE INTO quotes (contract_id, date, open, high, 
            low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)""", quotes)
        # Important to 'REPLACE' because last quote of download is incomplete,
        # if quote interval was unfinished. Needs to be replaced by complete
        # quote with overlapping subsequent quotes download
        conn.commit()
        cur.close()
        self.disconnect(conn)
        logger.debug(f"Inserted {len(quotes)} for contract_id {quotes[0][0]} "
                     f"into db.")

    def get_quotes(self, contract_id: int) -> pd.DataFrame:
        """Get quotes from the db

        :param contract_id: Contract ID to supply quotes for
        :type contract_id: int
        :return: All quotes available from the database for the given contract
        :rtype: pd.DataFrame
        """

        query = f"""SELECT date, open, high, low, close, volume
                    FROM quotes
                    WHERE contract_id = {contract_id}
                    ORDER BY date ASC;"""
        conn = self.connect()
        df = pd.read_sql_query(query, conn)
        self.disconnect(conn)
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df = df.set_index('date')
        logger.debug(f"Read {len(df)} quotes for contract id {contract_id} "
                     f"from db.")
        return df
