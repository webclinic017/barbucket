import sqlite3
import pandas as pd
import numpy as np
from datetime import date

from barbucket.database import DatabaseConnector
from barbucket.config import get_config_value
from barbucket.universes import UniversesDatabase
from barbucket.tws import Tws
from barbucket.contracts import ContractsDatabase


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
            VALUES (?, ?, ?, ?)""",(
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
                    WHERE contract_id = ?;""", contract_id)
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

        conn = self.connect()
        cur = conn.cursor()

        for key, value in parameter_data.items():
            if value is not None:
                cur.execute(f"""UPDATE quotes_status
                    SET {key} = ?
                    WHERE contract_id = ?)""",
                    (value, contract_id))
                conn.commit()

        cur.close()
        self.disconnect(conn)



class Quotes():

    def __init__(self):
        self.__abort_tws_operation = False


    def get_contract_quotes(self, contract_id):
        quotes_db = QuotesDatabase()
        return quotes_db.get_quotes(contract_id=contract_id)


    def get_universe_quotes(self, universe):
        pass


    def fetch_historical_quotes(self, universe):
        # Instanciate necessary objects
        universe_db = UniversesDatabase()
        tws = Tws()
        contracts_db = ContractsDatabase()
        quotes_db = QuotesDatabase()
        quotes_status_db = QuotesStatusDatabase()

        # Get config constants
        REDOWNLOAD_DAYS = int(get_config_value('quotes',
            'redownload_days'))

        # Get universe members
        contract_ids = universe_db.get_universe_members(universe=universe)

        tws.connect()
        try:
            for contract_id in contract_ids:

                # Abort, don't process further contracts
                if (self.__abort_tws_operation is True)\
                    or (tws.has_error() is True):
                    print('Aborting operation.')
                    break

                # Get contracts data
                filters = {'contract_id': contract_id}
                columns = ['broker_symbol', 'exchange', 'currency']
                contract = contracts_db.get_contracts(filters = filters,
                    return_columns=columns)[0]
                quotes_status = quotes_status_db.get_quotes_status(contract_id)

                debug_string = contract['broker_symbol'] + '_' + contract['exchange']
                print(debug_string, end='')

                # Calculate length of requested data
                if quotes_status['status_code'] == 1:
                    start_date = (quotes_status['daily_quotes_requsted_till'])
                    end_date = date.today().strftime('%Y-%m-%d')
                    ndays = np.busday_count(start_date, end_date)
                    if ndays <= REDOWNLOAD_DAYS:
                        print(' Existing data is only ' + str(ndays) + 
                            ' days old. Contract aborted.')
                        print('-------------------------')
                        continue
                    if ndays > 360:
                        print(' Last Download is ' + str(ndays) + 
                            ' days old. Contract aborted.')
                        print('-------------------------')
                        continue
                    ndays += 6
                    duration_str = str(ndays) + ' D'
                    quotes_from = quotes_status['daily_quotes_requsted_from']
                    quotes_till = end_date
                else:
                    duration_str = "15 Y"
                    quotes_from = date.today()
                    quotes_from.year -= 15
                    quotes_till = date.today().strftime('%Y-%m-%d')

                # Request quotes from tws
                quotes = tws.download_historical_data(
                    contract_id=contract_id,
                    symbol=contract['broker_symbol'],
                    exchange=contract['exchange'],
                    currency=contract['currency'],
                    duration=duration_str)

                # Inserting quotes into database
                quotes_db.insert_quotes(quotes=quotes)

                # Write finished info to contracts database
                quotes_status_db.update_quotes_status(
                    contract_id=contract_id,
                    status_code=1,
                    status_text="Successful",
                    daily_quotes_requested_from=quotes_from,
                    daily_quotes_requested_till=quotes_till)
                print(' Data stored.', end='')

        except KeyboardInterrupt:
            print('Keyboard interrupt detected.', end='')
            self.__abort_tws_operation = True

        finally:
            tws.disconnect()
            print('Disconnected.')