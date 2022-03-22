import logging
import logging.handlers

import click

from barbucket.builders.contracts_sync_processor_builder import build_contracts_sync_processor
from barbucket.builders.contract_details_ib_processor_builder import build_contract_details_ib_processor
from barbucket.builders.contract_details_tv_processor_builder import build_contract_details_tv_processor
from barbucket.builders.quotes_processor_builder import build_quotes_processor
from barbucket.builders.universe_processor_builder import build_universe_processor
from barbucket.domain_model.types import Exchange, ContractType

_logger = logging.getLogger(__name__)


@click.group()
# Initial group. This method is called to run the cli.
@click.option("-v", "--verbose", count=True, default=0, help="-v for DEBUG")
def cli(verbose) -> None:
    if verbose > 0:  # -v -> 1, -vv -> 2, etc.
        root_logger = logging.getLogger()
        root_logger.handlers[0].level = logging.DEBUG  # Dirty


# @click.group()
# # Initial group. This method is called to run the cli.
# def cli() -> None:
#     pass


# Group contracts
@cli.group()
def contracts() -> None:
    """Contracts commands"""


@contracts.command()
@click.option("-t", "--type", "contract_type", required=True, type=str)
@click.option("-e", "--exchange", "exchange", required=True, type=str)
def sync_listing(contract_type: str, exchange: str) -> None:
    """Sync master listing to IB exchange listing"""
    _logger.debug(
        f"User requested to sync '{contract_type}' contracts on '{exchange}' "
        f"to master listing via the cli.")
    try:
        ex = _create_exchange(exchange.upper())
        ct = _create_contract_type(contract_type.upper())
    except KeyError:
        pass
    else:
        contracts_sync_processor = build_contracts_sync_processor()
        contracts_sync_processor.sync_contracts_to_listing(exchange=ex)


@contracts.command()
def download_ib_details() -> None:
    """Fetch details for all contracts from IB TWS"""
    _logger.debug(
        f"User requested to download details from TWS via the cli.")
    ib_details_processor = build_contract_details_ib_processor()
    ib_details_processor.update_ib_contract_details()


@contracts.command()
def read_tv_details() -> None:
    """Read details for all contracts from TV files"""

    _logger.debug(
        f"User requested to read and store details from tv files via the cli.")
    tv_details_processor = build_contract_details_tv_processor()
    tv_details_processor.update_tv_contract_details()


# Group quotes
@cli.group()
def quotes() -> None:
    """Quotes commands"""


@quotes.command()
@click.option("-u", "--universe", "universe", required=True, type=str)
def fetch(universe: str) -> None:
    """Fetch quotes from IB TWS"""

    universe = universe.upper()
    _logger.debug(
        f"User requested to download quotes from TWS for universe "
        f"'{universe}' via the cli.")
    ib_quotes_processor = build_quotes_processor()
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

    _logger.debug(f"User requested to create universe '{name}' with "
                  f"{len(contract_ids)} members via the cli.")
    universes_processor = build_universe_processor()
    universes_processor.create_universe(name=name, contract_ids=contract_ids)


@universes.command(name="list")
def list_() -> None:
    """List existing universes"""

    _logger.debug(
        f"User requested to list all existing universes via the cli.")
    universes_processor = build_universe_processor()
    universes_processor.get_universes()


# @universes.command()
# @click.option("-n", "--name", "name", required=True, type=str)
# def members(name: str) -> None:
#     """List universes members"""

#     name = name.upper()
#     _logger.debug(
#         f"User requested to list the members of universe '{name}' via the cli.")
#     universes_db_connector = build_universe_db_manager()
#     members = universes_db_connector.get_members(universe=name)
#     if members:
#         _logger.info(f"Members of universe '{name}': {members}")
#     else:
#         _logger.info(f"Universe '{name}' does not exist.")


@universes.command()
@click.option("-n", "--name", "name", required=True, type=str)
def delete(name: str) -> None:
    """Delete universe"""

    _logger.debug(
        f"User requested to delete the universe '{name}' via the cli.")
    universes_processor = build_universe_processor()
    universes_processor.delete_universe(name=name)


# ~~~~~~~~~~~~~~~~~~~~~ private functions ~~~~~~~~~~~~~~~~~~~~~


def _create_exchange(name: str) -> Exchange:
    try:
        exchange = Exchange[name]
    except KeyError:
        exchanges = [ex.name for ex in Exchange]
        click.echo(f"Unknown exchange '{name}'. Known exchanges are: "
                   f"{exchanges}")
        raise KeyError
    else:
        return exchange


def _create_contract_type(name: str) -> ContractType:
    try:
        contract_type = ContractType[name]
    except KeyError:
        contract_types = [ct.name for ct in ContractType]
        click.echo(f"Unknown contract type '{name}'. Known contract types "
                   f"are: {contract_types}")
        raise KeyError
    else:
        return contract_type
