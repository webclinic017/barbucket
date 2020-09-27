import numpy as np
from datetime import date, timedelta
from datetime import datetime
import os
from pathlib import Path

from barbucket.database import DatabaseConnector
from barbucket.contracts import ContractsDatabase, IbExchangeListings
from barbucket.universes import UniversesDatabase
from barbucket.quotes import QuotesDatabase, QuotesStatusDatabase
from barbucket.tws import Tws
from barbucket.contract_details_tv import TvDetailsDatabase, TvDetailsFile
from barbucket.contract_details_ib import IbDetailsDatabse
from barbucket.config import get_config_value
from barbucket.tools import Tools


class AppInterface():

    def __init__(self):
        # If database file does not exist, initialize it
        if not Path.is_file(DatabaseConnector.DB_PATH):
            self.init_database()

        self.__abort_tws_operation = False


    def init_database(self):
        # backup old database if exists
        if Path.is_file(DatabaseConnector.DB_PATH):
            now = datetime.now()
            timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
            new_name = Path.home() / f".barbucket/database_backup_{timestamp}.db"
            DatabaseConnector.DB_PATH.rename(new_name)

        # create new database and connect to
        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE contracts (
                contract_id INTEGER NOT NULL PRIMARY KEY,
                contract_type_from_listing TEXT,
                exchange_symbol TEXT, 
                broker_symbol TEXT, 
                name TEXT,
                currency TEXT, 
                exchange TEXT);""")

        cur.execute("""
            CREATE TABLE contract_details_ib (
                contract_id INTEGER UNIQUE,
                contract_type_from_details TEXT,
                primary_exchange TEXT,
                industry TEXT,
                category TEXT,
                subcategory TEXT,
                FOREIGN KEY (contract_id)
                    REFERENCES contracts (contract_id)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE,
                UNIQUE (contract_id));""")

        cur.execute("""
            CREATE TABLE contract_details_tv (
                contract_id INTEGER UNIQUE,
                market_cap INTEGER,
                avg_vol_30_in_curr INTEGER,
                country TEXT,
                employees INTEGER,
                profit INTEGER,
                revenue INTEGER,
                FOREIGN KEY (contract_id)
                    REFERENCES contracts (contract_id)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE,
                UNIQUE (contract_id));""")

        cur.execute("""
            CREATE VIEW all_contract_info AS
                SELECT * FROM contracts
                    LEFT JOIN contract_details_ib ON
                        contracts.contract_id = contract_details_ib.contract_id
                    LEFT JOIN contract_details_tv ON
                        contracts.contract_id = contract_details_tv.contract_id
                    LEFT JOIN quotes_status ON
                        contracts.contract_id = quotes_status.contract_id;""")
            # Todo: remove 'contract_id' columns of subtables

        cur.execute("""
            CREATE TABLE quotes (
                contract_id INTEGER,
                date TEXT,
                open REAL,
                high REAL, 
                low REAL, 
                close REAL,
                volume REAL,
                FOREIGN KEY (contract_id)
                    REFERENCES contracts (contract_id)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE,
                UNIQUE (contract_id, date));""")

        cur.execute("""
            CREATE TABLE quotes_status (
                contract_id INTEGER UNIQUE,
                status_code INTEGER,
                status_text TEXT,
                daily_quotes_requested_from TEXT,
                daily_quotes_requested_till TEXT,
                FOREIGN KEY (contract_id)
                    REFERENCES contracts (contract_id)
                        ON UPDATE CASCADE
                        ON DELETE CASCADE,
                UNIQUE (contract_id));""")

        cur.execute("""
            CREATE TABLE universe_memberships (
                membership_id INTEGER NOT NULL PRIMARY KEY,
                contract_id INTEGER,
                universe TEXT);""")

        conn.commit()
        cur.close()
        db_connector.disconnect(conn)


    def get_contracts(self, filters={}, return_columns=[]):
        contracts_db = ContractsDatabase()
        contracts = contracts_db.get_contracts(filters=filters,
            return_columns=return_columns)
        return contracts


    def sync_contracts_to_listing(self, ctype, exchange):
        # Todo: Return statistics

        # Get all contracts from websites
        print(f'exchange: {exchange}')
        ib_listings = IbExchangeListings()
        website_data = []
        if ctype == "ETF":
            website_data = ib_listings.read_ib_exchange_listing_singlepage(ctype, exchange)
        elif ctype == "STOCK":
            website_data = ib_listings.read_ib_exchange_listing_paginated(ctype, exchange)

        # Get all contracts from database
        contracts_database = ContractsDatabase()
        filters = {'contract_type_from_listing': ctype, 'exchange': exchange}
        columns = ['broker_symbol', 'currency']
        database_data = contracts_database.get_contracts(filters=filters,
            return_columns=columns)

        # Delete contracts from database, that are not present in website
        contracts_removed = 0
        for db_row in database_data:
            exists = False
            for web_row in website_data:
                if (db_row['broker_symbol'] == web_row['broker_symbol']) and \
                    (db_row['currency'] == web_row['currency']):
                    exists = True
                    break
            if not exists:
                print('deleting: ' + db_row['broker_symbol'] + ' - ' + exchange)
                contracts_database.delete_contract(
                    symbol=db_row['broker_symbol'], \
                    exchange=exchange.upper(),
                    currency=db_row['currency'])
                contracts_removed += 1
        print('contracts removed: ' + str(contracts_removed))

        # Add contracts from website to database, that are not present in database
        contracts_added = 0
        for web_row in website_data:
            exists = False
            for db_row in database_data:
                if (web_row['broker_symbol'] == db_row['broker_symbol']) and\
                    (web_row['currency'] == db_row['currency']):
                    exists = True
                    break
            if not exists:
                print('creating: ' + web_row['broker_symbol'] + ' - ' + exchange)
                contracts_database.create_contract(
                    contract_type_from_listing=ctype,
                    exchange_symbol=web_row['exchange_symbol'],
                    broker_symbol=web_row['broker_symbol'],
                    name=web_row['name'],
                    currency=web_row['currency'],
                    exchange=exchange.upper())
                contracts_added += 1
        print('contracts added: ' + str(contracts_added))


    def ingest_tv_files(self):
        # Instanciate necessary objects
        tv_details_db = TvDetailsDatabase()
        tv_details_file = TvDetailsFile()
        contracts_db = ContractsDatabase()
        tools = Tools()
        
        # Create list of path+filename of all files in directory
        dir_path = Path.home() / ".barbucket/tv_screener"
        tv_screener_files = [
            os.path.join(dir_path, f) for f in os.listdir(dir_path) if
            os.path.isfile(os.path.join(dir_path, f))]

        # Iterate over files in directory
        for tv_file in tv_screener_files:
            file_data = tv_details_file.get_data_from_file(file=tv_file)

            for row in file_data:
                # Find corresponding contract id
                ticker = row['ticker'].replace(".", " ")
                filters = {'primary_exchange': \
                    tools.decode_exchange_tv(row['exchange']),
                    'contract_type_from_listing': "STOCK",
                    'exchange_symbol': ticker}
                columns = ['contract_id']
                result = contracts_db.get_contracts(
                    filters=filters,
                    return_columns=columns)

                if len(result) == 1:

                    # Write details to db
                    contract_id = result[0]['contract_id']
                    tv_details_db.insert_tv_details(
                        contract_id=contract_id,
                        market_cap=row['market_cap'],
                        avg_vol_30_in_curr=row['avg_vol_30_in_curr'],
                        country=row['country'],
                        employees=row['employees'],
                        profit=row['profit'],
                        revenue=row['revenue'])
                else:
                    ticker =row['ticker']
                    exchange = row['exchange']
                    print(f"Error: {len(result)} results for {ticker} \
                        on {exchange}.")


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
        tools = Tools()

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
                if quotes_status is None:
                    quotes_status = {'status_code': 0}

                if quotes_status['status_code'] == 1:
                    start_date = (quotes_status['daily_quotes_requested_till'])
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
                    fifteen_years = timedelta(days=5479)
                    quotes_from -= fifteen_years
                    quotes_till = date.today().strftime('%Y-%m-%d')

                # Request quotes from tws
                quotes = tws.download_historical_quotes(
                    contract_id=contract_id,
                    symbol=contract['broker_symbol'],
                    exchange=tools.encode_exchange_ib(contract['exchange']),
                    currency=contract['currency'],
                    duration=duration_str)

                if quotes is not None:
                    # Inserting quotes into database
                    quotes_db.insert_quotes(quotes=quotes)

                    # Write finished info to contracts database
                    quotes_status_db.insert_quotes_status(
                        contract_id=contract_id,
                        status_code=1,
                        status_text="Successful",
                        daily_quotes_requested_from=quotes_from,
                        daily_quotes_requested_till=quotes_till)
                    print(' Data stored.', end='')

                else:
                    # Write error info to contracts database
                    # Todo: See error-method of Tws-class
                    pass

                print("Finished.")

        except KeyboardInterrupt:
            print('Keyboard interrupt detected.', end='')
            self.__abort_tws_operation = True

        finally:
            tws.disconnect()
            print('Disconnected.')


    def fetch_ib_contract_details(self,):

        contracts_db = ContractsDatabase()
        columns = ['contract_id', 'contract_type_from_listing',
            'broker_symbol', 'exchange', 'currency']
        filters = {'market_cap': "NULL"}
        contracts = contracts_db.get_contracts(filters=filters,
            return_columns=columns)

        if contracts is None:
            print("No contracts with IB details missing.")
            return

        tws = Tws()
        ib_details_db = IbDetailsDatabse()
        tws.connect()

        try:
            for contract in contracts:
                # Abort, don't process further contracts
                if (self.__abort_tws_operation is True)\
                    or (tws.has_error() is True):
                    print('Aborting operation.')
                    break

                contract_details = tws.download_contract_details(
                    contract_type_from_listing=contract['contract_type_from_listing'],
                    broker_symbol=contract['broker_symbol'],
                    exchange=contract['exchange'],
                    currency=contract['currency'])

                ib_details_db.insert_ib_details(
                    contract_id=contract['contract_id'],
                    contract_type_from_details=contract_details.stockType,
                    primary_exchange=contract_details.contract.primaryExchange,
                    industry=contract_details.industry,
                    category=contract_details.category,
                    subcategory=contract_details.subcategory)

            tws.disconnect()

        except KeyboardInterrupt:
            print('Keyboard interrupt detected.', end='')
            self.__abort_tws_operation = True

        finally:
            tws.disconnect()
            print('Disconnected.')


    def create_universe(self, name, contract_ids):
        universes = UniversesDatabase()
        universes.create_universe(name=name, contract_ids=contract_ids)


    def get_universes(self,):
        universes = UniversesDatabase()
        result = universes.get_universes()
        return result


    def get_universe_members(self, universe):
        universes = UniversesDatabase()
        members = universes.get_universe_members(universe)
        return members


    def delete_universe(self, universe):
        universes = UniversesDatabase()
        universes.delete_universe(universe)
