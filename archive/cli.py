import logging
import logging.handlers
from pathlib import Path

import click

from .universes_db_connector import UniversesDbConnector
from .ib_exchange_listings_processor import IbExchangeListingsProcessor
from .ib_details_processor import IbDetailsProcessor
from .tv_details_processor import TvDetailsProcessor
from .ib_quotes_processor import IbQuotesProcessor
from .encodings import Exchange


logger = logging.getLogger(__name__)


@click.group()
# Initial group. This method is called to run the cli.
@click.option("-v", "--verbose", count=True, default=0, help="-v for DEBUG")
def cli(verbose) -> None:
    if verbose > 0:  # -v -> 1, -vv -> 2, etc.
        root_logger = logging.getLogger()
        root_logger.handlers[0].level = logging.DEBUG  # Dirty


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
    if validate_exchange(exchange.upper()):
        ib_exchange_listings_processor = IbExchangeListingsProcessor()
        ib_exchange_listings_processor.sync_contracts_to_listing(
            ctype=contract_type.upper(),
            exchange=exchange.upper()
        )


@contracts.command()
def download_ib_details() -> None:
    """Fetch details for all contracts from IB TWS"""
    logger.debug(
        f"User requested to download details from TWS via the cli.")
    ib_details_processor = IbDetailsProcessor()
    ib_details_processor.update_ib_contract_details()


@contracts.command()
def read_tv_details() -> None:
    """Read details for all contracts from TV files"""

    logger.debug(
        f"User requested to read and store details from tv files via the cli.")
    tv_details_processor = TvDetailsProcessor()
    tv_details_processor.read_tv_data()


# Group quotes
@cli.group()
def quotes() -> None:
    """Quotes commands"""


@quotes.command()
@click.option("-u", "--universe", "universe", required=True, type=str)
def fetch(universe: str) -> None:
    """Fetch quotes from IB TWS"""

    universe = universe.upper()
    logger.debug(
        f"User requested to download quotes from TWS for universe "
        f"'{universe}' via the cli.")
    ib_quotes_processor = IbQuotesProcessor()
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

    name = name.upper()
    logger.debug(
        f"User requested to create universe '{name}' with {len(contract_ids)} "
        f"members via the cli.")
    con_list = [int(n) for n in contract_ids.split(",")]
    universes_db_connector = UniversesDbConnector()
    universes_db_connector.create_universe(
        name=name,
        contract_ids=con_list)
    logger.info(f"Created universe '{name}' with {len(con_list)} contracts.")


@universes.command()
def list() -> None:
    """List all universes"""

    logger.debug(
        f"User requested to list all existing universes via the cli.")
    universes_db_connector = UniversesDbConnector()
    universes = universes_db_connector.get_universes()
    if universes:
        logger.info(f"Existing universes: {universes}")
    else:
        logger.info(f"No existing universes")


@universes.command()
@click.option("-n", "--name", "name", required=True, type=str)
def members(name: str) -> None:
    """List universes members"""

    name = name.upper()
    logger.debug(
        f"User requested to list the members of universe '{name}' via the cli.")
    universes_db_connector = UniversesDbConnector()
    members = universes_db_connector.get_universe_members(universe=name)
    if members:
        logger.info(f"Members of universe '{name}': {members}")
    else:
        logger.info(f"Universe '{name}' does not exist.")


@universes.command()
@click.option("-n", "--name", "name", required=True, type=str)
@click.confirmation_option(
    prompt=("Are you sure you want to delete this universe?"))
def delete(name: str) -> None:
    """Delete universe"""

    name = name.upper()
    logger.debug(
        f"User requested to delete the universe '{name}' via the cli.")
    universes_db_connector = UniversesDbConnector()
    n_affeced_rows = universes_db_connector.delete_universe(universe=name)
    if n_affeced_rows > 0:
        logger.info(
            f"Deleted universe '{name}' with {n_affeced_rows} members.")
    else:
        logger.info(f"Universe '{name}' did not exist.")


def validate_exchange(exchange) -> bool:
    exchanges = [member.name for member in Exchange]
    if not exchange in exchanges:
        logger.info(f"'{exchange}' is not a valid exchange. Valid exchanges "
                    f"are: {exchanges}")
        return False
    return True
