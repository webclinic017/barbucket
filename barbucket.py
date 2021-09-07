import logging

from barbucket.config_initializer import ConfigInitializer
from barbucket.config_reader import ConfigReader
from barbucket.db_initializer import DbInitializer
from barbucket.db_connector import DbConnector
from barbucket.contracts_db_connector import ContractsDbConnector
from barbucket.universes_db_connector import UniversesDbConnector
from barbucket.quotes_db_connector import QuotesDbConnector
from barbucket.quotes_status_db_connector import QuotesStatusDbConnector
from barbucket.tws_connector import TwsConnector
from barbucket.ib_exchange_listings_processor import IbExchangeListingsProcessor
from barbucket.ib_details_processor import IbDetailsProcessor
from barbucket.tv_details_processor import TvDetailsProcessor
from barbucket.encoder import Encoder
from barbucket.graceful_exiter import GracefulExiter
from barbucket.cli import CommandLineInterface
from barbucket.mediator import Mediator


if __name__ == '__main__':
    """Docstring"""

    # Setup logging
    FORMAT = "%(message)s"
    logging.basicConfig(format=FORMAT, level=logging.INFO)

    # Create mediator
    mediator = Mediator(
        config_initializer=ConfigInitializer(),
        config_reader=ConfigReader(),
        db_initializer=DbInitializer(),
        db_connector=DbConnector(),
        contracts_db_connector=ContractsDbConnector(),
        universe_db_connector=UniversesDbConnector(),
        quotes_db_connector=QuotesDbConnector(),
        quotes_status_db_connector=QuotesStatusDbConnector(),
        tws_connector=TwsConnector(),
        ib_listings_processor=IbExchangeListingsProcessor(),
        ib_details_processor=IbDetailsProcessor(),
        tv_details_processor=TvDetailsProcessor(),
        encoder=Encoder(),
        exiter=GracefulExiter(),
        cli=CommandLineInterface())

    # Initialize config and db files and folders
    mediator.notify("initalize_config")
    mediator.notify("initialize_database")

    # Run Cli
    mediator.notify("run_cli")
