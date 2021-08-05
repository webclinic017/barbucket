from datetime import date, timedelta
import os
from pathlib import Path
import logging

import enlighten
import numpy as np

from barbucket.database import DatabaseConnector
from barbucket.contracts import ContractsDatabase, IbExchangeListings
from barbucket.universes import UniversesDatabase
from barbucket.quotes import QuotesDatabase, QuotesStatusDatabase
from barbucket.tws import Tws
from barbucket.contract_details_tv import TvDetailsDatabase, TvDetailsFile
from barbucket.contract_details_ib import IbDetailsDatabase
from barbucket.config import Config
from barbucket.tools import Tools, GracefulExiter


# Setup logging
FORMAT = "%(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


class AppInterface():

    def __init__(self):
        # Instanciate necessary objects
        self.db_connector = DatabaseConnector()
        self.contracts_db = ContractsDatabase()
        self.ib_listings = IbExchangeListings()
        self.ib_details_db = IbDetailsDatabase()
        self.tv_details_db = TvDetailsDatabase()
        self.tv_details_file = TvDetailsFile()
        self.quotes_db = QuotesDatabase()
        self.quotes_status_db = QuotesStatusDatabase()
        self.universe_db = UniversesDatabase()
        self.tws = Tws()
        self.config = Config()
        self.exiter = GracefulExiter()
        self.tools = Tools()


        # Initialize database (create if not exists)
        self.init_database()


    def archive_database(self):
        self.db_connector.archive_database()


    def get_contracts(self, filters={}, return_columns=[]):
        contracts = self.contracts_db.get_contracts(filters=filters,
            return_columns=return_columns)
        return contracts


    def sync_contracts_to_listing(self, ctype, exchange):
        logging.info(f'Syncing {ctype} contracts on {exchange} to master listing.')
        # Get all contracts from websites
        website_data = []
        if ctype == "ETF":
            website_data = self.ib_listings.read_ib_exchange_listing_singlepage(ctype, exchange)
        elif ctype == "STOCK":
            website_data = self.ib_listings.read_ib_exchange_listing_paginated(ctype, exchange)

        # Abort, if webscraping was aborted by user
        if website_data == []:
            return

        # Get all contracts from database
        filters = {'contract_type_from_listing': ctype, 'exchange': exchange}
        columns = ['broker_symbol', 'currency']
        database_data = self.contracts_database.get_contracts(filters=filters,
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
                self.contracts_database.delete_contract(
                    symbol=db_row['broker_symbol'], \
                    exchange=exchange.upper(),
                    currency=db_row['currency'])
                contracts_removed += 1
        logging.info(f'{contracts_removed} contracts removed from master listing.')

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
                self.contracts_database.create_contract(
                    contract_type_from_listing=ctype,
                    exchange_symbol=web_row['exchange_symbol'],
                    broker_symbol=web_row['broker_symbol'],
                    name=web_row['name'],
                    currency=web_row['currency'],
                    exchange=exchange.upper())
                contracts_added += 1
        logging.info(f'{contracts_added} contracts added to master listing.')


    def ingest_tv_files(self):

        # Create list of path+filename of all files in directory
        dir_path = Path.home() / ".barbucket/tv_screener"
        tv_screener_files = [
            os.path.join(dir_path, f) for f in os.listdir(dir_path) if
            # os.path.isfile(os.path.join(dir_path, f))]
            f.endswith(".csv")]

        # Iterate over files in directory
        for tv_file in tv_screener_files:
            logging.info(f"Ingesting TV file {tv_file}.")
            file_data = self.tv_details_file.get_data_from_file(file=tv_file)

            for row in file_data:
                # Find corresponding contract id
                ticker = row['ticker'].replace(".", " ")
                filters = {'exchange': \
                    self.tools.decode_exchange_tv(row['exchange']),
                    'contract_type_from_listing': "STOCK",
                    'exchange_symbol': ticker}
                columns = ['contract_id']
                result = self.contracts_db.get_contracts(
                    filters=filters,
                    return_columns=columns)

                if len(result) == 1:

                    # Write details to db
                    contract_id = result[0]['contract_id']
                    self.tv_details_db.insert_tv_details(
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
                    logging.warning(f"{len(result)} contracts found in master listing for '{ticker}' on '{exchange}'.")


    def get_contract_quotes(self, contract_id):
        return self.quotes_db.get_quotes(contract_id=contract_id)


    def get_universe_quotes(self, universe):
        pass


    def fetch_historical_quotes(self, universe):
        logging.info(f"Fetching historical quotes for universe {universe}.")

        # Get config constants
        REDOWNLOAD_DAYS = int(self.config.get_config_value_single('quotes',
            'redownload_days'))

        # Get universe members
        contract_ids = self.universe_db.get_universe_members(universe=universe)

        # Setup progress bar
        manager = enlighten.get_manager()
        pbar = manager.counter(total=len(contract_ids), desc="Contracts", unit="contracts")

        self.tws.connect()
        logging.info(f"Connnected to TWS.")

        try:
            for contract_id in contract_ids:

                # Abort, don't process further contracts
                if self.exiter.exit() or self.tws.has_error():
                    logging.info("Aborting historical quotes fetching.")
                    break

                # Get contracts data
                filters = {'contract_id': contract_id}
                columns = ['broker_symbol', 'exchange', 'currency']
                contract = self.contracts_db.get_contracts(filters = filters,
                    return_columns=columns)[0]
                quotes_status = self.quotes_status_db.get_quotes_status(contract_id)
                logging.info(f"Preparing to fetch hiostorical quotes for {contract['broker_symbol']} on {contract['exchange']}")

                # Calculate length of requested data
                if quotes_status is None:
                    duration_str = "15 Y"
                    quotes_from = date.today()
                    fifteen_years = timedelta(days=5479)
                    quotes_from -= fifteen_years
                    quotes_till = date.today().strftime('%Y-%m-%d')

                elif quotes_status['status_code'] == 1:
                    start_date = (quotes_status['daily_quotes_requested_till'])
                    end_date = date.today().strftime('%Y-%m-%d')
                    ndays = np.busday_count(start_date, end_date)
                    if ndays <= REDOWNLOAD_DAYS:
                        logging.info(f"Existing data is only {ndays} days old. Contract aborted.")
                        pbar.total -= 1
                        pbar.update(incr=0)
                        continue
                    if ndays > 360:
                        logging.info(f"Existing data is already {ndays} days old. Contract aborted.")
                        pbar.total -= 1
                        pbar.update(incr=0)
                        continue
                    ndays += 6
                    duration_str = str(ndays) + ' D'
                    quotes_from = quotes_status['daily_quotes_requested_from']
                    quotes_till = end_date

                else:
                    logging.info("Contract already has error status. Skipped.")
                    pbar.total -= 1
                    pbar.update(incr=0)
                    continue

                # Request quotes from tws
                quotes = self.tws.download_historical_quotes(
                    contract_id=contract_id,
                    symbol=contract['broker_symbol'],
                    exchange=self.tools.encode_exchange_ib(contract['exchange']),
                    currency=contract['currency'],
                    duration=duration_str)

                if quotes is not None:
                    # Inserting quotes into database
                    logging.info(f"Storing {len(quotes)} quotes to database.")
                    self.quotes_db.insert_quotes(quotes=quotes)

                    # Write finished info to contracts database
                    self.quotes_status_db.insert_quotes_status(
                        contract_id=contract_id,
                        status_code=1,
                        status_text="Successful",
                        daily_quotes_requested_from=quotes_from,
                        daily_quotes_requested_till=quotes_till)

                else:
                    # Write error info to contracts database
                    error_code, error_text = self.tws.get_contract_error()
                    self.quotes_status_db.insert_quotes_status(
                        contract_id=contract_id,
                        status_code=error_code,
                        status_text=error_text,
                        daily_quotes_requested_from=None,
                        daily_quotes_requested_till=None)                
                pbar.update()

            logging.info(f"Finished fetching historical quotes for universe {universe}.")

        finally:
            self.tws.disconnect()
            logging.info(f"Disconnnected from TWS.")


    def fetch_ib_contract_details(self,):
        columns = ['contract_id', 'contract_type_from_listing',
            'broker_symbol', 'exchange', 'currency']
        filters = {'primary_exchange': "NULL"}
        contracts = self.contracts_db.get_contracts(filters=filters,
            return_columns=columns)
        logging.info(f"Found {len(contracts)} contracts with missing IB details in master listing.")

        if len(contracts) == 0:
            return

        # Setup progress bar
        manager = enlighten.get_manager()
        pbar = manager.counter(total=len(contracts), desc="Contracts", unit="contracts")

        self.tws.connect()
        logging.info(f"Connnected to TWS.")

        try:
            for contract in contracts:
                # Check for abort conditions
                if self.exiter.exit() or self.tws.has_error():
                    logging.info(f"Abort fetching of IB details.")
                    break

                contract_details = self.tws.download_contract_details(
                    contract_type_from_listing=contract['contract_type_from_listing'],
                    broker_symbol=contract['broker_symbol'],
                    exchange=contract['exchange'],
                    currency=contract['currency'])

                if contract_details is not None:
                    self.ib_details_db.insert_ib_details(
                        contract_id=contract['contract_id'],
                        contract_type_from_details=contract_details.stockType,
                        primary_exchange=contract_details.contract.primaryExchange,
                        industry=contract_details.industry,
                        category=contract_details.category,
                        subcategory=contract_details.subcategory)

                pbar.update()

        finally:
            self.tws.disconnect()
            logging.info(f"Disconnnected from TWS.")


    def create_universe(self, name, contract_ids):
        self.universes.create_universe(name=name, contract_ids=contract_ids)


    def get_universes(self,):
        result = self.universes.get_universes()
        return result


    def get_universe_members(self, universe):
        members = self.universes.get_universe_members(universe)
        return members


    def delete_universe(self, universe):
        self.universes.delete_universe(universe)
