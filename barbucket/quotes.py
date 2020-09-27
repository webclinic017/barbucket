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
        # Todo: Sanitize query

        query = f"""SELECT date, open, high, low, close, volume
                    FROM quotes
                    WHERE contract_id = {contract_id}
                    ORDER BY date ASC;"""

        db_connection = DatabaseConnector()
        conn = db_connection.connect()
        df = pd.read_sql_query(query, conn)
        db_connection.disconnect(conn)

        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
            # more flexible to provide just strings
        df = df.set_index('date')

        return df


    # def delete_quotes_before_date(self, contract_id, date):
    #     conn = self.connect()
    #     cur = conn.cursor()
    #     cur.execute(f"""DELETE FROM quotes
    #                     WHERE (contract_id = {contract_id}
    #                         AND date(date) <= '{date}')""")
    #     conn.commit()
    #     cur.close()
    #     self.disconnect(conn)


class QuotesStatusDatabase():

    def __init__(self):
        pass


    def create_empty_quotes_status(self, contract_id):
        db_connection = DatabaseConnector()
        conn = db_connection.connect()
        cur = conn.cursor()

        cur.execute("""INSERT INTO quotes_status (
            contract_id,
            status_code,
            status_text,
            daily_quotes_requested_from, 
            daily_quotes_requested_till) 
            VALUES (?, ?, ?, ?, ?)""",(
            contract_id,
            None,
            None,
            None,
            None))

        conn.commit()
        cur.close()
        db_connection.disconnect(conn)


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

        # Todo: Do not check for error
        if len(result) > 0:
            return result[0]
        else:
            return None


    def update_quotes_status(self, contract_id, status_code, status_text,
        daily_quotes_requested_from, daily_quotes_requested_till):
        """ Status code:
        1: Successfully downloaded quotes
        >1: TWS error code
        """

        # Update new data to database
        parameter_data = {'status_code': status_code,
            'status_text': status_text,
            'daily_quotes_requested_from': daily_quotes_requested_from,
            'daily_quotes_requested_till': daily_quotes_requested_till}

        db_connection = DatabaseConnector()
        conn = db_connection.connect()
        cur = conn.cursor()

        for key, value in parameter_data.items():
            if value is not None:
                cur.execute(f"""UPDATE quotes_status
                    SET {key} = ?
                    WHERE contract_id = ?""",
                    (value, contract_id))
                conn.commit()

        cur.close()
        db_connection.disconnect(conn)
