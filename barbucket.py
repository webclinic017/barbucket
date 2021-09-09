import logging
import logging.handlers

from pathlib import Path

from barbucket.mediator import Mediator
from barbucket.config_initializer import ConfigInitializer
from barbucket.config_reader import ConfigReader
from barbucket.db_initializer import DbInitializer
from barbucket.db_connector import DbConnector
from barbucket.contracts_db_connector import ContractsDbConnector
from barbucket.universes_db_connector import UniversesDbConnector
from barbucket.quotes_db_connector import QuotesDbConnector
from barbucket.quotes_status_db_connector import QuotesStatusDbConnector
from barbucket.ib_details_connector import IbDetailsConnector
from barbucket.tws_connector import TwsConnector
from barbucket.ib_exchange_listings_processor import IbExchangeListingsProcessor
from barbucket.ib_details_processor import IbDetailsProcessor
from barbucket.tv_details_processor import TvDetailsProcessor
from barbucket.graceful_exiter import GracefulExiter
from barbucket import cli as cli, ib_details_connector


if __name__ == '__main__':
    """Docstring"""

    # Setup logging
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARN)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=Path.home() / ".barbucket/logfile.log",
        when='midnight')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    logger = logging.getLogger(__name__)
    logger.info("Application started.")

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
        ib_details_connector=IbDetailsConnector(),
        tws_connector=TwsConnector(),
        ib_listings_processor=IbExchangeListingsProcessor(),
        ib_details_processor=IbDetailsProcessor(),
        tv_details_processor=TvDetailsProcessor(),
        exiter=GracefulExiter(),
        cli=cli
    )

    # Initialize config and db files and folders
    mediator.notify("initalize_config")
    mediator.notify("initialize_database")

    # Run Cli
    mediator.notify("run_cli")
