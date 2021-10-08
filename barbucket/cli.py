import logging
from typing import Any

import click

from .base_component import BaseComponent
from .custom_exceptions import ExitSignalDetectedError
"""
The click cli is not designed to be declared within a class. So its functions
are declared in the module without a class. Then a CliConnector class is 
instanciated as a module-wide object and referenced for the mediator 
communication.
"""

logger = logging.getLogger(__name__)


class CliConnector(BaseComponent):
    def __init__(self, mediator: Any = None) -> None:
        self.mediator = mediator


cli_connector = CliConnector()


# Initial group. This method is called to run the cli.
@click.group()
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
    logger.info(
        f"User requested to sync '{contract_type}' contracts on '{exchange}' "
        f"to master listing via the cli.")
    cli_connector.mediator.notify(
        "sync_contracts_to_listing",
        {'ctype': contract_type.upper(),
            'exchange': exchange.upper()})


@contracts.command()
def download_ib_details() -> None:
    """Fetch details for all contracts from IB TWS"""
    logger.info(
        f"User requested to download details from TWS via the cli.")
    cli_connector.mediator.notify("update_ib_contract_details")


@contracts.command()
def read_tv_details() -> None:
    """Read details for all contracts from TV files"""
    logger.info(
        f"User requested to read and store details from tv files via the cli.")
    file_count = cli_connector.mediator.notify("read_tv_data")
    click.echo(f"Finished reading {file_count} TV files.")


# Group quotes
@cli.group()
def quotes() -> None:
    """Quotes commands"""


@quotes.command()
@click.option("-u", "--universe", "universe", required=True, type=str)
def fetch(universe: str) -> None:
    """Fetch quotes from IB TWS"""
    logger.info(
        f"User requested to download quotes from TWS for universe "
        f"'{universe}' via the cli.")
    cli_connector.mediator.notify(
        "download_historical_quotes",
        {'universe': universe})


# Group universes
@cli.group()
def universes() -> None:
    """Universes commands"""


@universes.command()
@click.option("-n", "--name", "name", required=True, type=str)
@click.option("-c", "--contract_ids", "contract_ids", required=True, type=str)
def create(name: str, contract_ids: str) -> None:
    """Create new universe"""
    logger.info(
        f"User requested to create universe '{name}' with {len(contract_ids)} "
        f"members via the cli.")
    con_list = [int(n) for n in contract_ids.split(",")]
    cli_connector.mediator.notify(
        "create_universe",
        {'name': name, 'contract_ids': con_list})
    click.echo(
        f"Created universe '{name}' with {len(contract_ids)} members.")


@universes.command()
def list() -> None:
    """List all universes"""
    logger.info(f"User requestet to list all universes via the cli.")
    universes = cli_connector.mediator.notify("get_universes")
    click.echo(universes)


@universes.command()
@click.option("-n", "--name", "name", required=True, type=str)
def members(name: str) -> None:
    """List universes members"""
    logger.info(
        f"User requestet to list the members for universe '{name}' via the "
        f"cli.")
    members = cli_connector.mediator.notify(
        "get_universe_members",
        {'universe': name})
    click.echo(members)


@universes.command()
@click.option("-n", "--name", "name", required=True, type=str)
@click.confirmation_option(
    prompt=("Are you sure you want to delete this universe?"))
def delete(name: str) -> None:
    """Delete universe"""
    logger.info(
        f"User requestet to delete universe '{name}' via the cli.")
    cli_connector.mediator.notify(
        "delete_universe",
        {'universe': name})
    click.echo(f"Deleted universe '{name}'.")


# Callbacks
def show_messeage(message: str) -> None:
    click.echo(message)
