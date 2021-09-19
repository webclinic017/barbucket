from typing import List, Any
import logging

import pandas as pd

from .mediator import Mediator

logger = logging.getLogger(__name__)


class QuotesDbConnector():
    """Provides methods to access the 'quotes' table of the database."""

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator

    def insert_quotes(self, quotes: List[Any]) -> None:
        """Insert quotes into the db"""

        conn = self.mediator.notify("get_db_connection")
        cur = conn.cursor()
        cur.executemany("""REPLACE INTO quotes (contract_id, date, open, high, 
            low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)""", quotes)
        # Important to 'REPLACE' because last quote of download is incomplete,
        # if quote interval was unfinished. Needs to be replaced by complete
        # quote with overlapping subsequent quotes download
        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})
        logger.debug(f"Inserted {len(quotes)} for contract_id {quotes[0][0]} "
                     f"into db.")

    def get_quotes(self, contract_id: int) -> pd.DataFrame:
        """Get quotes from the db"""

        query = f"""SELECT date, open, high, low, close, volume
                    FROM quotes
                    WHERE contract_id = {contract_id}
                    ORDER BY date ASC;"""
        conn = self.mediator.notify("get_db_connection")
        df = pd.read_sql_query(query, conn)
        self.mediator.notify("close_db_connection", {'conn': conn})
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df = df.set_index('date')
        logger.debug(f"Read {len(df)} quotes for contract id {contract_id} "
                     f"from db.")
        return df
