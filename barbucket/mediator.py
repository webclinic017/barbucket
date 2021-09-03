from datetime import date, timedelta
import os
from pathlib import Path
from typing import Optional

from .database import DatabaseInitializer, DatabaseConnector
from .contracts import ContractsDatabase, IbExchangeListings
from .universes import UniversesDatabase
from .quotes import QuotesDatabase, QuotesStatusDatabase
from .tws import Tws
from .tv_details_processor import TvDetailsProcessor
from .ib_details_processor import IbDetailsProcessor
from .config import ConfigInitializer, ConfigReader
from .tools import Tools, GracefulExiter
from .base_component import BaseComponent


class Mediator():
    """Mediator"""

    def __init__(
            self,
            db_initializer: DatabaseInitializer,
            db_connector: DatabaseConnector,
            contracts_db: ContractsDatabase,
            ib_listings: IbExchangeListings,
            ib_details_processor: IbDetailsProcessor,
            tv_details_processor: TvDetailsProcessor,
            quotes_db: QuotesDatabase,
            quotes_status_db: QuotesStatusDatabase,
            universe_db: UniversesDatabase,
            tws: Tws,
            config_initializer: ConfigInitializer,
            config_reader: ConfigReader,
            exiter: GracefulExiter,
            tools: Tools) -> None:

        # Instanciate components
        self.__db_initializer = db_initializer
        self.__db_initializer.mediator = self

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

        self.__config_initializer = config_initializer
        self.__config_initializer.mediator = self

        self.__config_reader = config_reader
        self.__config_reader.mediator = self

        self.__exiter = exiter
        self.__exiter.mediator = self

        self.__tools = tools
        self.__tools.mediator = self

    def notify(self, action: str, parameters: dict = {}) -> Optional[object]:
        # ContractsDatabase
        if action == "get_contracts":
            return self.__contracts_db.get_contracts(
                filters=parameters['filters'],
                return_columns=parameters['return_columns'])
        # DatabaseInitializer
        elif action == "initialize_database":
            return self.__db_initializer.initialize_database()
        # DatabaseConnector
        elif action == "get_db_connection":
            return self.__db_connector.connect()
        elif action == "close_db_connection":
            return self.__db_connector.disconnect(
                conn=parameters['conn'])
        # Tools
        elif action == "decode_exchange_tv":
            return self.__tools.decode_exchange_tv(
                exchange=parameters['exchange'])
        # Tws
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
        elif action == "tws_has_error":
            return self.__tws.has_error()
        elif action == "download_historical_quotes":
            return self.__tws.download_historical_quotes(
                contract_id=parameters['contract_id'],
                symbol=parameters['symbol'],
                exchange=parameters['exchange'],
                currency=parameters['currency'],
                duration=parameters['duration'])
        elif action == "get_tws_contract_error":
            return self.__tws.get_contract_error()
        # GracefulExiter
        elif action == "exit_signal":
            return self.__exiter.exit()
        # ConfigInitializer
        elif action == "initalize_config":
            return self.__config_initializer.initalize_config()
        # ConfigReader
        elif action == "get_config_value_single":
            return self.__config_reader.get_config_value_single(
                section=parameters['section'],
                option=parameters['option'])
        elif action == "get_config_value_list":
            return self.__config_reader.get_config_value_list(
                section=parameters['section'],
                option=parameters['option'])
        # UniversesDatabase
        elif action == "get_universe_members":
            return self.__universe_db.get_universe_members(
                universe=parameters['universe'])
        elif action == "create_universe":
            return self.__universe_db.create_universe(
                name=parameters['name'],
                contract_ids=parameters['contract_ids'])
        elif action == "get_universes":
            return self.__universe_db.get_universes()
        elif action == "delete_universe":
            return self.__universe_db.delete_universe(
                universe=parameters['universe'])
        # QuotesDatabase
        elif action == "insert_quotes":
            return self.__quotes_db.insert_quotes(
                quotes=parameters['quotes'])
        # QuotesStatusDatabase
        elif action == "insert_quotes_status":
            return self.__quotes_status_db.insert_quotes_status(
                contract_id=parameters['contract_id'],
                status_code=parameters['status_code'],
                status_text=parameters['status_text'],
                daily_quotes_requested_from=parameters['daily_quotes_requested_from'],
                daily_quotes_requested_till=parameters['daily_quotes_requested_till'])
        # IbExchangeListings
        elif action == "sync_contracts_to_listing":
            return self.__ib_listings.sync_contracts_to_listing(
                ctype=parameters['ctype'],
                exchange=parameters['exchange'])
        # IbDetailsProc
        elif action == "update_ib_contract_details":
            return self.__ib_details_processor.update_ib_contract_details()
        # TvDetailsProc
        elif action == "read_tv_data":
            return self.__tv_details_processor.read_tv_data()
