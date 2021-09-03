import logging

import click

from barbucket.database import DatabaseInitializer, DatabaseConnector
from barbucket.contracts import ContractsDatabase, IbExchangeListings
from barbucket.universes import UniversesDatabase
from barbucket.quotes import QuotesDatabase, QuotesStatusDatabase
from barbucket.tws import Tws
from barbucket.tv_details_processor import TvDetailsProcessor
from barbucket.ib_details_processor import IbDetailsProcessor
from barbucket.config import ConfigInitializer, ConfigReader
from barbucket.tools import Tools, GracefulExiter
from barbucket.base_component import BaseComponent
from barbucket.mediator import Mediator


class CommandLineInterface():
    """Docstring"""

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator

    # Initial group, not explicitly called
    @click.group()
    def cli(self):
        pass

    # Group database
    @cli.group()
    def database(self):
        """Local database commands"""

    @database.command()
    @click.confirmation_option(prompt="Are you sure you want to archive the current database?")
    def archive(self):
        """Archive the local database"""
        self.mediator.notify("archive_database")
        click.echo("Successfully archived database.")

    # Group contracts
    @cli.group()
    def contracts(self):
        """Contracts commands"""

    @contracts.command()
    @click.option("-t", "--type", "contract_type", required=True, type=str)
    @click.option("-e", "--exchange", "exchange", required=True, type=str)
    def sync_listing(self, contract_type, exchange):
        """Sync master listing to IB exchange listing"""
        self.mediator.notify(
            "sync_contracts_to_listing",
            {'ctype': contract_type.upper(),
             'exchange': exchange.upper()})
        click.echo(f"Master listing synced for {contract_type.upper()} on "
                   f"{exchange.upper()}.")

    @contracts.command()
    def download_ib_details(self):
        """Fetch details for all contracts from IB TWS"""
        self.mediator.notify("update_ib_contract_details")
        click.echo("Updated IB details for master listings.")

    @contracts.command()
    def read_tv_details(self):
        """Read details for all contracts from TV files"""
        self.mediator.notify("read_tv_data")
        click.echo(f"Finished reading TV files.")

    # Group quotes
    @cli.group()
    def quotes(self):
        """Quotes commands"""

    @quotes.command()
    @click.option("-u", "--universe", "universe", required=True, type=str)
    def fetch(self, universe):
        """Fetch quotes from IB TWS"""
        self.mediator.notify(
            "download_historical_quotes",
            {'universe': universe})
        click.echo(f"Finished collecting historical data for universe: "
                   f"{universe}")

    # Group universes
    @cli.group()
    def universes(self):
        """Universes commands"""

    @universes.command()
    @click.option("-n", "--name", "name", required=True, type=str)
    @click.option("-c", "--contract_ids", "contract_ids", required=True, type=str)
    def create(self, name, contract_ids):
        """Create new universe"""
        con_list = [int(n) for n in contract_ids.split(",")]
        self.mediator.notify(
            "create_universe",
            {'name': name, 'contract_ids': con_list})
        click.echo(f"Created universe {name}.")

    @universes.command()
    def list(self):
        """List all universes"""
        universes = self.mediator.notify("get_universes")
        click.echo(f"{universes}")

    @universes.command()
    @click.option("-n", "--name", "name", required=True, type=str)
    def members(self, name):
        """List universes members"""
        members = self.mediator.notify(
            "get_universe_members",
            {'universe': name})
        click.echo(f"{members}")

    @universes.command()
    @click.option("-n", "--name", "name", required=True, type=str)
    @click.confirmation_option(prompt="Are you sure you want to delete this universe?")
    def delete(self, name):
        """Delete universe"""
        self.mediator.notify(
            "delete_universe",
            {'universe': name})
        click.echo(f"Deleted universe {name}.")


if __name__ == '__main__':
    """Docstring"""

    # Setup logging
    FORMAT = "%(message)s"
    logging.basicConfig(format=FORMAT, level=logging.INFO)

    # db_initializer = DatabaseInitializer()
    # db_connector = DatabaseConnector()
    # contracts_db = ContractsDatabase()
    # ib_listings = IbExchangeListings()
    # ib_details_processor = IbDetailsProcessor()
    # tv_details_processor = TvDetailsProcessor()
    # quotes_db = QuotesDatabase()
    # quotes_status_db = QuotesStatusDatabase()
    # universe_db = UniversesDatabase()
    # tws = Tws()
    # config_initializer = ConfigInitializer()
    # config_reader = ConfigReader()
    # exiter = GracefulExiter()
    # tools = Tools()

    mediator = Mediator(
        db_initializer=DatabaseInitializer(),
        db_connector=DatabaseConnector(),
        contracts_db=ContractsDatabase(),
        ib_listings=IbExchangeListings(),
        ib_details_processor=IbDetailsProcessor(),
        tv_details_processor=TvDetailsProcessor(),
        quotes_db=QuotesDatabase(),
        quotes_status_db=QuotesStatusDatabase(),
        universe_db=UniversesDatabase(),
        tws=Tws(),
        config_initializer=ConfigInitializer(),
        config_reader=ConfigReader(),
        exiter=GracefulExiter(),
        tools=Tools())

    # Initialize
    mediator.notify("initalize_config")
    mediator.notify("initialize_database")

    # Cli
    cli = CommandLineInterface()
    cli.cli()
