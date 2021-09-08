from typing import Optional, Any

from . import cli as cli


class Mediator():
    """Mediator"""

    def __init__(
            self,
            config_initializer: Any,
            config_reader: Any,
            db_initializer: Any,
            db_connector: Any,
            contracts_db_connector: Any,
            universe_db_connector: Any,
            quotes_db_connector: Any,
            quotes_status_db_connector: Any,
            tws_connector: Any,
            ib_listings_processor: Any,
            ib_details_processor: Any,
            tv_details_processor: Any,
            encoder: Any,
            exiter: Any,
            cli: Any) -> None:

        # Instanciate components
        self.__config_initializer = config_initializer
        self.__config_initializer.mediator = self

        self.__config_reader = config_reader
        self.__config_reader.mediator = self

        self.__db_initializer = db_initializer
        self.__db_initializer.mediator = self

        self.__db_connector = db_connector
        self.__db_connector.mediator = self

        self.__contracts_db_connector = contracts_db_connector
        self.__contracts_db_connector.mediator = self

        self.__universe_db_connector = universe_db_connector
        self.__universe_db_connector.mediator = self

        self.__quotes_db_connector = quotes_db_connector
        self.__quotes_db_connector.mediator = self

        self.__quotes_status_db_connector = quotes_status_db_connector
        self.__quotes_status_db_connector.mediator = self

        self.__tws_connector = tws_connector
        self.__tws_connector.mediator = self

        self.__ib_listings_processor = ib_listings_processor
        self.__ib_listings_processor.mediator = self

        self.__ib_details_processor = ib_details_processor
        self.__ib_details_processor.mediator = self

        self.__tv_details_processor = tv_details_processor
        self.__tv_details_processor.mediator = self

        self.__encoder = encoder
        self.__encoder.mediator = self

        self.__exiter = exiter
        self.__exiter.mediator = self

        self.__cli = cli
        self.__cli.cli_connector.mediator = self

    def notify(self, action: str, parameters: dict = {}) -> Optional[object]:
        # ConfigInitializer
        if action == "initalize_config":
            return self.__config_initializer.initalize_config()
        # ConfigReader
        elif action == "get_config_value_single":
            return self.__config_reader.get_config_value_single(
                section=parameters['section'],
                option=parameters['option'])
        # DbInitializer
        elif action == "initialize_database":
            return self.__db_initializer.initialize_database()
        # DbConnector
        elif action == "get_db_connection":
            return self.__db_connector.connect()
        elif action == "close_db_connection":
            return self.__db_connector.disconnect(
                conn=parameters['conn'])
        # ContractsDbConnector
        elif action == "get_contracts":
            return self.__contracts_db_connector.get_contracts(
                filters=parameters['filters'],
                return_columns=parameters['return_columns'])
        elif action == "create_contract":
            return self.__contracts_db_connector.create_contract(
                contract_type_from_listing=parameters['contract_type_from_listing'],
                exchange_symbol=parameters['exchange_symbol'],
                broker_symbol=parameters['broker_symbol'],
                name=parameters['name'],
                currency=parameters['currency'],
                exchange=parameters['exchange'])
        # UniversesDbConnector
        elif action == "get_universe_members":
            return self.__universe_db_connector.get_universe_members(
                universe=parameters['universe'])
        elif action == "create_universe":
            return self.__universe_db_connector.create_universe(
                name=parameters['name'],
                contract_ids=parameters['contract_ids'])
        elif action == "get_universes":
            return self.__universe_db_connector.get_universes()
        elif action == "delete_universe":
            return self.__universe_db_connector.delete_universe(
                universe=parameters['universe'])
        # QuotesDbConnector
        elif action == "insert_quotes":
            return self.__quotes_db_connector.insert_quotes(
                quotes=parameters['quotes'])
        # QuotesStatusDbConnector
        elif action == "insert_quotes_status":
            return self.__quotes_status_db_connector.insert_quotes_status(
                contract_id=parameters['contract_id'],
                status_code=parameters['status_code'],
                status_text=parameters['status_text'],
                daily_quotes_requested_from=parameters['daily_quotes_requested_from'],
                daily_quotes_requested_till=parameters['daily_quotes_requested_till'])
        # TwsConnector
        elif action == "download_contract_details_from_tws":
            return self.__tws_connector.download_contract_details(
                contract_type_from_listing=parameters['contract_type_from_listing'],
                broker_symbol=parameters['broker_symbol'],
                exchange=parameters['exchange'],
                currency=parameters['currency'])
        elif action == "connect_to_tws":
            return self.__tws_connector.connect()
        elif action == "disconnect_from_tws":
            return self.__tws_connector.disconnect()
        elif action == "tws_has_error":
            return self.__tws_connector.has_error()
        elif action == "download_historical_quotes":
            return self.__tws_connector.download_historical_quotes(
                contract_id=parameters['contract_id'],
                symbol=parameters['symbol'],
                exchange=parameters['exchange'],
                currency=parameters['currency'],
                duration=parameters['duration'])
        elif action == "get_tws_contract_error":
            return self.__tws_connector.get_contract_error()
        # IbExchangeListingsProcessor
        elif action == "sync_contracts_to_listing":
            return self.__ib_listings_processor.sync_contracts_to_listing(
                ctype=parameters['ctype'],
                exchange=parameters['exchange'])
        # IbDetailsProcessor
        elif action == "update_ib_contract_details":
            return self.__ib_details_processor.update_ib_contract_details()
        # TvDetailsProcessor
        elif action == "read_tv_data":
            return self.__tv_details_processor.read_tv_data()
        # Tools
        elif action == "decode_exchange_tv":
            return self.__encoder.decode_exchange_tv(
                exchange=parameters['exchange'])
        # GracefulExiter
        elif action == "exit_requested_by_user":
            return self.__exiter.exit_requested()
        elif action == "get_config_value_list":
            return self.__config_reader.get_config_value_list(
                section=parameters['section'],
                option=parameters['option'])
        # Cli
        elif action == "run_cli":
            return self.__cli.cli()
        elif action == "exiter_send_user_message":
            return self.__cli.exiter_message()
