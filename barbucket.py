import logging
import logging.handlers
from pathlib import Path

import click

from barbucket.universes_db_connector import UniversesDbConnector
from barbucket.ib_exchange_listings_processor import IbExchangeListingsProcessor
from barbucket.ib_details_processor import IbDetailsProcessor
from barbucket.tv_details_processor import TvDetailsProcessor
from barbucket.ib_quotes_processor import IbQuotesProcessor


universes_db_connector = UniversesDbConnector()
ib_exchange_listings_processor = IbExchangeListingsProcessor()
ib_details_processor = IbDetailsProcessor()
tv_details_processor = TvDetailsProcessor()
ib_quotes_processor = IbQuotesProcessor()


@click.group()
# Initial group. This method is called to run the cli.
def cli() -> None:
    pass


# Group contracts
@cli.group()
def contracts() -> None:
    """Contracts commands"""


@contracts.command()
@click.option("-t", "--type", "contract_type", required=True, type=str)
@click.option("-e", "--exchange", "exchange", required=True, type=str)
def sync_listing(contract_type: str, exchange: str) -> None:
    """Sync master listing to IB exchange listing"""
    logger.debug(
        f"User requested to sync '{contract_type}' contracts on '{exchange}' "
        f"to master listing via the cli.")
    ib_exchange_listings_processor.sync_contracts_to_listing(
        ctype=contract_type.upper(),
        exchange=exchange.upper()
    )


@contracts.command()
def download_ib_details() -> None:
    """Fetch details for all contracts from IB TWS"""
    logger.debug(
        f"User requested to download details from TWS via the cli.")
    ib_details_processor.update_ib_contract_details()


@contracts.command()
def read_tv_details() -> None:
    """Read details for all contracts from TV files"""
    logger.debug(
        f"User requested to read and store details from tv files via the cli.")
    file_count = tv_details_processor.read_tv_data()
    logger.info(f"Finished reading {file_count} TV files.")


# Group quotes
@cli.group()
def quotes() -> None:
    """Quotes commands"""


@quotes.command()
@click.option("-u", "--universe", "universe", required=True, type=str)
def fetch(universe: str) -> None:
    """Fetch quotes from IB TWS"""
    logger.debug(
        f"User requested to download quotes from TWS for universe "
        f"'{universe}' via the cli.")
    ib_quotes_processor.download_historical_quotes(
        universe=universe)


# Group universes
@cli.group()
def universes() -> None:
    """Universes commands"""


@universes.command()
@click.option("-n", "--name", "name", required=True, type=str)
@click.option("-c", "--contract_ids", "contract_ids", required=True, type=str)
def create(name: str, contract_ids: str) -> None:
    """Create new universe"""
    logger.debug(
        f"User requested to create universe '{name}' with {len(contract_ids)} "
        f"members via the cli.")
    con_list = [int(n) for n in contract_ids.split(",")]
    universes_db_connector.create_universe(
        name=name,
        contract_ids=con_list)
    logger.info(
        f"Created universe '{name}' with {len(contract_ids)} members.")


@universes.command()
def list() -> None:
    """List all universes"""
    logger.debug(f"User requested to list all universes via the cli.")
    universes = universes_db_connector.get_universes()
    logger.info(universes)


@universes.command()
@click.option("-n", "--name", "name", required=True, type=str)
def members(name: str) -> None:
    """List universes members"""
    logger.debug(
        f"User requested to list the members for universe '{name}' via the "
        f"cli.")
    members = universes_db_connector.get_universe_members(
        universe=name)
    logger.info(members)


@universes.command()
@click.option("-n", "--name", "name", required=True, type=str)
@click.confirmation_option(
    prompt=("Are you sure you want to delete this universe?"))
def delete(name: str) -> None:
    """Delete universe"""
    logger.debug(
        f"User requested to delete universe '{name}' via the cli.")
    universes_db_connector.delete_universe(universe=name)
    logger.info(f"Deleted universe '{name}'.")


if __name__ == '__main__':
    """Docstring"""

    # Setup logging
    def my_filenamer(filename):
        new_name = filename.replace(".txt.", "_") + ".txt"
        return new_name

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=Path.home() / ".barbucket/logfile.txt",
        when='midnight')
    file_handler.namer = my_filenamer
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s;%(name)s;%(levelname)s;%(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    logger = logging.getLogger(__name__)
    logger.debug("Application started.")

    # Run Cli
    cli()
