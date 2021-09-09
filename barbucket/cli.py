import logging
from typing import Any

import click

from .base_component import BaseComponent

"""
The click cli is not designed to be declared within a class. So it's functions
are declared in the module without a class. Then a MediatorConnector class is 
instanciated as a module-wide object and referenced for the mediator 
communication.
"""


class CliConnector(BaseComponent):
    def __init__(self, mediator: Any = None) -> None:
        self.mediator = mediator


cli_connector = CliConnector()


# Initial group. This method is called to run the cli.
@click.group()
def cli() -> None:
    pass


# Group database
@cli.group()
def database() -> None:
    """Local database commands"""


@database.command()
@click.confirmation_option(prompt="Are you sure you want to archive the current database?")
def archive() -> None:
    """Archive the local database"""
    logging.info(f"User requested to archive the datebase cia the cli.")
    cli_connector.mediator.notify("archive_database")
    click.echo("Successfully archived database.")


# Group contracts
@cli.group()
def contracts() -> None:
    """Contracts commands"""


@contracts.command()
@click.option("-t", "--type", "contract_type", required=True, type=str)
@click.option("-e", "--exchange", "exchange", required=True, type=str)
def sync_listing(contract_type: str, exchange: str) -> None:
    """Sync master listing to IB exchange listing"""
    logging.info(f"User requested to sync '{contract_type}' contracts on "
                 f"'{exchange}' to master listing via the cli.")
    cli_connector.mediator.notify(
        "sync_contracts_to_listing",
        {'ctype': contract_type.upper(),
            'exchange': exchange.upper()})
    click.echo(f"Master listing synced for {contract_type.upper()} on "
               f"{exchange.upper()}.")


@contracts.command()
def download_ib_details() -> None:
    """Fetch details for all contracts from IB TWS"""
    logging.info(f"User requested to download details from TWS via the cli"
                 f".")
    cli_connector.mediator.notify("update_ib_contract_details")
    click.echo("Updated IB details for master listings.")


@contracts.command()
def read_tv_details() -> None:
    """Read details for all contracts from TV files"""
    logging.info(f"User requested to read and store details from tv files "
                 f"via the cli.")
    cli_connector.mediator.notify("read_tv_data")
    click.echo(f"Finished reading TV files.")


# Group quotes
@cli.group()
def quotes() -> None:
    """Quotes commands"""


@quotes.command()
@click.option("-u", "--universe", "universe", required=True, type=str)
def fetch(universe: str) -> None:
    """Fetch quotes from IB TWS"""
    logging.info(f"User requested to download quotes from TWS for "
                 f"universe '{universe}' via the cli.")
    cli_connector.mediator.notify(
        "download_historical_quotes",
        {'universe': universe})
    click.echo(f"Finished downloading historical data for universe "
               f"'{universe}'")


# Group universes
@cli.group()
def universes() -> None:
    """Universes commands"""


@universes.command()
@click.option("-n", "--name", "name", required=True, type=str)
@click.option("-c", "--contract_ids", "contract_ids", required=True, type=str)
def create(name: str, contract_ids: str) -> None:
    """Create new universe"""
    logging.info(f"User requested to create universe '{name}' with "
                 f"{len(contract_ids)} members via the cli.")
    con_list = [int(n) for n in contract_ids.split(",")]
    cli_connector.mediator.notify(
        "create_universe",
        {'name': name, 'contract_ids': con_list})
    click.echo(f"Created universe '{name}' with {len(contract_ids)} "
               f"members.")


@universes.command()
def list() -> None:
    """List all universes"""
    logging.info(f"User requestet to list all universes via the cli.")
    universes = cli_connector.mediator.notify("get_universes")
    click.echo(universes)


@universes.command()
@click.option("-n", "--name", "name", required=True, type=str)
def members(name: str) -> None:
    """List universes members"""
    logging.info(f"User requestet to list the members for universe "
                 f"'{name}' via the cli.")
    members = cli_connector.mediator.notify(
        "get_universe_members",
        {'universe': name})
    click.echo(members)


@universes.command()
@click.option("-n", "--name", "name", required=True, type=str)
@click.confirmation_option(prompt="Are you sure you want to delete this universe?")
def delete(name: str) -> None:
    """Delete universe"""
    logging.info(f"User requestet to delete universe '{name}' via the "
                 f"cli.")
    cli_connector.mediator.notify(
        "delete_universe",
        {'universe': name})
    click.echo(f"Deleted universe '{name}'.")


# Callbacks
def show_messeage(message: str) -> None:
    click.echo(message)
