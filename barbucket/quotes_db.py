import sqlite3
import os
from ib_insync import contract
import pandas as pd
import numpy as np
from datetime import datetime


from barbucket.database import DataBase
from barbucket.config import get_config_value
from barbucket.universes_db import UniversesDB
from barbucket.tws_connector import TwsConnector
from barbucket.contracts_db import ContractsDB


class QuotesDB(DataBase):

    def __init__(self):
        self.__universes_db = UniversesDB
        self.__tws_connector = TwsConnector
        self.__contracts_db = ContractsDB

        self.__abort_operation = False



    def insert_quotes(self, quotes):
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



    def get_quotes(self, contract_id):

        query = f"""SELECT date, open, high, low, close, volume
                    FROM quotes
                    WHERE contract_id = {contract_id}
                    ORDER BY date ASC;"""

        conn = self.connect()
        df = pd.read_sql_query(query, conn)
        self.disconnect(conn)

        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
            # more flexible to provide just strings
        df = df.set_index('date')

        return df



    def delete_quotes_before_date(self, contract_id, date):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(f"""DELETE FROM quotes
                        WHERE (contract_id = {contract_id}
                            AND date(date) <= '{date}')""")
        conn.commit()
        cur.close()
        self.disconnect(conn)



    def get_quotes_status(self, contract_id):
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""SELECT *
                    FROM quotes_status
                    WHERE contract_id = ?;""", contract_id)
        result = cur.fetchall()

        conn.commit()
        cur.close()
        self.disconnect(conn)

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

        # If no entry exists, create an empty one
        if self.get_quotes_status(contract_id) == None:
            conn = self.connect()
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
            self.disconnect(conn)

        # Update new data to database
        parameter_data = {'status_code': status_code,
            'status_text': status_text,
            'daily_quotes_requested_from': daily_quotes_requested_from,
            'daily_quotes_requested_till': daily_quotes_requested_till}

        conn = self.connect()
        cur = conn.cursor()

        for column, value in parameter_data.items():
            if value is not None:
                cur.execute(f"""UPDATE quotes_status
                    SET {column} = ?
                    WHERE contract_id = ?)""",
                    (value, contract_id))
                conn.commit()

        cur.close()
        self.disconnect(conn)



    def download_quotes(self, universe):
        # Get config constants
        REDOWNLOAD_DAYS = int(get_config_value('quotes',
            'redownload_days'))

        # Get universe members
        contract_ids = self.__universes_db.get_universe_members(universe)

        self.__tws_connector.connect()
        try:    
            for contract_id in contract_ids:

                # Abort, don't process further contracts
                if (self.__abort_operation is True)\
                    or (self.__tws_connector.has_error() is True):
                    print('Aborting operation.')
                    break

                # Get contracts data
                filters = {'contract_id': contract_id}
                columns = ['broker_symbol', 'exchange', 'currency']
                contract = self.__contracts_db.get_contracts(filters = filters,
                    return_columns=columns)[0]
                existing_quotes = self.get_quotes_status(contract_id)

                debug_string = contract['broker_symbol'] + '_' + contract['exchange']
                print(debug_string, end='')

                # Calculate length of requested data
                if existing_quotes['status_code'] == 1:
                    start_date = (existing_quotes['daily_quotes_requsted_till'])
                    end_date = datetime.today().strftime('%Y-%m-%d')
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
                else:
                    duration_str = "15 Y"

                # Request quotes from tws
                quotes = self.__tws_connector.get_historical_data(
                    contract_id=contract_id,
                    symbol=contract['broker_symbol'],
                    exchange=contract['exchange'],
                    currency=contract['currency'],
                    duration=duration_str)

                # Inserting quotes into database
                self.__quotes_db.insert_quotes(quotes=quotes)

                # Write finished info to contracts database
                timestamp_now = datetime.now()
                string_now = timestamp_now.strftime('%Y-%m-%d')
                status_text = 'downloaded:' + string_now
                self.__contracts_db.update_contract_status(
                    symbol=contract['broker_symbol'],
                    exchange=contract['exchange'],
                    currency=contract['currency'],
                    status_code=1,
                    status_text=status_text
                )
                print(' Data stored.', end='')

        except KeyboardInterrupt:
            print('Keyboard interrupt detected.', end='')
            self.__abort_operation = True

        finally:
            self.__tws_connector.disconnect()
            print('Disconnected.')