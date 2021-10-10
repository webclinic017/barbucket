from typing import Optional, Any

from . import cli as cli


class Mediator():
    """Mediator"""

    def __init__(
            self,
            tws_connector: Any,
            ib_listings_processor: Any,
            ib_details_processor: Any,
            tv_details_processor: Any,
            cli: Any) -> None:

        # Instanciate components
        self.__tws_connector = tws_connector
        self.__tws_connector.mediator = self

        self.__ib_listings_processor = ib_listings_processor
        self.__ib_listings_processor.mediator = self

        self.__ib_details_processor = ib_details_processor
        self.__ib_details_processor.mediator = self

        self.__tv_details_processor = tv_details_processor
        self.__tv_details_processor.mediator = self

        self.__cli = cli
        self.__cli.cli_connector.mediator = self

    def notify(self, action: str, parameters: dict = {}) -> Optional[object]:
        # TwsConnector
        if action == "download_contract_details_from_tws":
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
        # Cli
        elif action == "run_cli":
            return self.__cli.cli()
        elif action == "show_cli_message":
            return self.__cli.show_messeage(
                message=parameters['message'])
