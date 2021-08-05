import sqlite3

import pandas as pd

from barbucket.database import DatabaseConnector


class QuotesDatabase():

    def __init__(self):
        pass

    def insert_quotes(self, quotes):
        db_connection = DatabaseConnector()
        conn = db_connection.connect()
        cur = conn.cursor()

        cur.executemany("""REPLACE INTO quotes (contract_id, date, open, high, 
            low, close, volume) VALUES (?, ?, ?, ?, ?, ?, ?)""", quotes)
        # Important to 'REPLACE' because last quote of download is incomplete,
        # if quote interval was unfinished. Needs to be replaced by complete
        # quote with overlapping subsequent quotes download

        conn.commit()
        cur.close()
        db_connection.disconnect(conn)

    def get_quotes(self, contract_id):
        query = f"""SELECT date, open, high, low, close, volume
                    FROM quotes
                    WHERE contract_id = {contract_id}
                    ORDER BY date ASC;"""

        db_connection = DatabaseConnector()
        conn = db_connection.connect()
        df = pd.read_sql_query(query, conn)
        db_connection.disconnect(conn)

        # more flexible to provide just strings
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        df = df.set_index('date')

        return df


class QuotesStatusDatabase():

    def __init__(self):
        pass

    def get_quotes_status(self, contract_id):
        db_connection = DatabaseConnector()
        conn = db_connection.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""SELECT *
                    FROM quotes_status
                    WHERE contract_id = ?;""", (contract_id,))
        result = cur.fetchall()

        conn.commit()
        cur.close()
        db_connection.disconnect(conn)

        if len(result) > 0:
            return result[0]
        else:
            return None

    def insert_quotes_status(self, contract_id, status_code, status_text,
                             daily_quotes_requested_from,
                             daily_quotes_requested_till):
        """ Status code:
        1: Successfully downloaded quotes
        >1: TWS error code
        """

        existing_status = self.get_quotes_status(contract_id=contract_id)

        if (status_code is None) and (existing_status is not None):
            status_code = existing_status['status_code']
        if (status_text is None) and (existing_status is not None):
            status_text = existing_status['status_text']
        if (daily_quotes_requested_from is None) and (existing_status is not None):
            daily_quotes_requested_from = existing_status['daily_quotes_requested_from']
        if (daily_quotes_requested_till is None) and (existing_status is not None):
            daily_quotes_requested_till = existing_status['daily_quotes_requested_till']

        db_connection = DatabaseConnector()
        conn = db_connection.connect()
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
        db_connection.disconnect(conn)
