from datetime import date, timedelta
import os
from pathlib import Path
from typing import Optional

from .database import DatabaseConnector
from .contracts import ContractsDatabase, IbExchangeListings
from .universes import UniversesDatabase
from .quotes import QuotesDatabase, QuotesStatusDatabase
from .tws import Tws
from .tv_details_processor import TvDetailsProcessor
from .ib_details_processor import IbDetailsProcessor
from .config import Config
from .tools import Tools, GracefulExiter
from .base_component import BaseComponent


class Mediator():
    """Mediator"""

    def __init__(
            self,
            db_connector: DatabaseConnector,
            contracts_db: ContractsDatabase,
            ib_listings: IbExchangeListings,
            ib_details_processor: IbDetailsProcessor,
            tv_details_processor: TvDetailsProcessor,
            quotes_db: QuotesDatabase,
            quotes_status_db: QuotesStatusDatabase,
            universe_db: UniversesDatabase,
            tws: Tws,
            config: Config,
            exiter: GracefulExiter,
            tools: Tools) -> None:

        # Instanciate components
        self.__db_connector = db_connector
        self.__db_connector.mediator = self

        self.__contracts_db = contracts_db
        self.__contracts_db.mediator = self

        self.__ib_listings = ib_listings
        self.__ib_listings.mediator = self

        self.__ib_details_processor = ib_details_processor
        self.__ib_details_processor.mediator = self

        self.__tv_details_processor = tv_details_processor
        self.__tv_details_processor.mediator = self

        self.__quotes_db = quotes_db
        self.__quotes_db.mediator = self

        self.__quotes_status_db = quotes_status_db
        self.__quotes_status_db.mediator = self

        self.__universe_db = universe_db
        self.__universe_db.mediator = self

        self.__tws = tws
        self.__tws.mediator = self

        self.__config = config
        self.__config.mediator = self

        self.__exiter = exiter
        self.__exiter.mediator = self

        self.__tools = tools
        self.__tools.mediator = self

    def notify(self, action: str, parameters: dict = {}) -> Optional[object]:
        if action == "get_contracts":
            return self.__contracts_db.get_contracts(
                filters=parameters['filters'],
                return_columns=parameters['return_columns'])

        elif action == "get_db_connection":
            return self.__db_connector.connect()
        elif action == "close_db_connection":
            return self.__db_connector.disconnect(conn=parameters['conn'])
        elif action == "decode_exchange_tv":
            return self.__db_connector.connect(
                exchange=parameters['exchange'])

        elif action == "download_contract_details_from_tws":
            return self.__tws.download_contract_details(
                contract_type_from_listing=parameters['contract_type_from_listing'],
                broker_symbol=parameters['broker_symbol'],
                exchange=parameters['exchange'],
                currency=parameters['currency'])
        elif action == "connect_to_tws":
            return self.__tws.connect()
        elif action == "disconnect_from_tws":
            return self.__tws.disconnect()
        elif action == "tws_error":
            return self.__tws.has_error()

        elif action == "exit_signal":
            return self.__exiter.exit()

    # def fetch_historical_quotes(self, universe):
    #     logging.info(f"Fetching historical quotes for universe {universe}.")

    #     # Get config constants
    #     REDOWNLOAD_DAYS = int(self.config.get_config_value_single(
    #         'quotes',
    #         'redownload_days'))

    #     # Get universe members
    #     contract_ids = self.universe_db.get_universe_members(universe=universe)

    #     # Setup progress bar
    #     manager = enlighten.get_manager()
    #     pbar = manager.counter(
    #         total=len(contract_ids),
    #         desc="Contracts", unit="contracts")

    #     self.tws.connect()
    #     logging.info(f"Connnected to TWS.")

    #     try:
    #         for contract_id in contract_ids:

    #             # Abort, don't process further contracts
    #             if self.exiter.exit() or self.tws.has_error():
    #                 logging.info("Aborting historical quotes fetching.")
    #                 break

    #             # Get contracts data
    #             filters = {'contract_id': contract_id}
    #             columns = ['broker_symbol', 'exchange', 'currency']
    #             contract = self.contracts_db.get_contracts(
    #                 filters=filters,
    #                 return_columns=columns)[0]
    #             quotes_status = self.quotes_status_db.get_quotes_status(
    #                 contract_id)
    #             logging.info(
    #                 f"Preparing to fetch hiostorical quotes for {contract['broker_symbol']} on {contract['exchange']}")

    #             # Calculate length of requested data
    #             if quotes_status is None:
    #                 duration_str = "15 Y"
    #                 quotes_from = date.today()
    #                 fifteen_years = timedelta(days=5479)
    #                 quotes_from -= fifteen_years
    #                 quotes_till = date.today().strftime('%Y-%m-%d')

    #             elif quotes_status['status_code'] == 1:
    #                 start_date = (quotes_status['daily_quotes_requested_till'])
    #                 end_date = date.today().strftime('%Y-%m-%d')
    #                 ndays = np.busday_count(start_date, end_date)
    #                 if ndays <= REDOWNLOAD_DAYS:
    #                     logging.info(
    #                         f"Existing data is only {ndays} days old. Contract aborted.")
    #                     pbar.total -= 1
    #                     pbar.update(incr=0)
    #                     continue
    #                 if ndays > 360:
    #                     logging.info(
    #                         f"Existing data is already {ndays} days old. Contract aborted.")
    #                     pbar.total -= 1
    #                     pbar.update(incr=0)
    #                     continue
    #                 ndays += 6
    #                 duration_str = str(ndays) + ' D'
    #                 quotes_from = quotes_status['daily_quotes_requested_from']
    #                 quotes_till = end_date

    #             else:
    #                 logging.info("Contract already has error status. Skipped.")
    #                 pbar.total -= 1
    #                 pbar.update(incr=0)
    #                 continue

    #             # Request quotes from tws
    #             quotes = self.tws.download_historical_quotes(
    #                 contract_id=contract_id,
    #                 symbol=contract['broker_symbol'],
    #                 exchange=self.tools.encode_exchange_ib(
    #                     contract['exchange']),
    #                 currency=contract['currency'],
    #                 duration=duration_str)

    #             if quotes is not None:
    #                 # Inserting quotes into database
    #                 logging.info(f"Storing {len(quotes)} quotes to database.")
    #                 self.quotes_db.insert_quotes(quotes=quotes)

    #                 # Write finished info to contracts database
    #                 self.quotes_status_db.insert_quotes_status(
    #                     contract_id=contract_id,
    #                     status_code=1,
    #                     status_text="Successful",
    #                     daily_quotes_requested_from=quotes_from,
    #                     daily_quotes_requested_till=quotes_till)

    #             else:
    #                 # Write error info to contracts database
    #                 error_code, error_text = self.tws.get_contract_error()
    #                 self.quotes_status_db.insert_quotes_status(
    #                     contract_id=contract_id,
    #                     status_code=error_code,
    #                     status_text=error_text,
    #                     daily_quotes_requested_from=None,
    #                     daily_quotes_requested_till=None)
    #             pbar.update()

    #         logging.info(
    #             f"Finished fetching historical quotes for universe {universe}.")

    #     finally:
    #         self.tws.disconnect()
    #         logging.info(f"Disconnnected from TWS.")
