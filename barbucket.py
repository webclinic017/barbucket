import logging

import click

from barbucket.tv_details_processor import TvDetailsProcessor
from barbucket.mediator import Mediator


class CommandLineInterface():
    """Docstring"""

    def __init__(self) -> None:
        # Create component objects
        self.__tv_details_processor = TvDetailsProcessor()

        # Initialize database (create if not exists)
        self.db_connector.init_database()

    # Initial group, not explicitly called
    @click.group()
    def cli(self):
        pass

    # Group database
    @cli.group()
    def database(self):
        """Local database commands"""

    @database.command()
    @click.confirmation_option(prompt="Are you sure you want to archive the database?")
    def archive(self):
        """Archive the local database"""
        self.app.archive_database()
        click.echo("Archived database.")

    # Group contracts
    @cli.group()
    def contracts(self):
        """Contracts commands"""

    @contracts.command()
    @click.option("-t", "--type", "contract_type", required=True, type=str)
    @click.option("-e", "--exchange", "exchange", required=True, type=str)
    def sync_listing(self, contract_type, exchange):
        """Sync master listing to IB exchange listing"""
        self.app.sync_contracts_to_listing(
            ctype=contract_type.upper(), exchange=exchange.upper())
        click.echo(
            f"Master listing synced for {contract_type.upper()} on {exchange.upper()}.")

    @contracts.command()
    def fetch_ib_details(self):
        """Fetch details for all contracts from IB TWS"""
        self.app.fetch_ib_contract_details()
        click.echo("Updated IB details for master listings.")

    @contracts.command()
    def fetch_tv_details(self):
        """Fetch details for all contracts from TV files"""
        self.__tv_details_processor.read_tv_data()
        click.echo(f"Finished ingesting TV files.")

    # Group quotes
    @cli.group()
    def quotes(self):
        """Quotes commands"""

    @quotes.command()
    @click.option("-u", "--universe", "universe", required=True, type=str)
    def fetch(self, universe):
        """Fetch quotes from IB TWS"""
        self.app.fetch_historical_quotes(universe=universe)
        click.echo(
            f"Finished collecting historical data for universe: {universe}")

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
        self.app.create_universe(name=name, contract_ids=con_list)
        click.echo(f"Created universe {name}.")

    @universes.command()
    def list(self):
        """List all universes"""
        result = self.app.get_universes()
        click.echo(f"Existing universes: {result}.")

    @universes.command()
    @click.option("-n", "--name", "name", required=True, type=str)
    def members(self, name):
        """List universes members"""
        members = self.app.get_universe_members(universe=name)
        click.echo(f"Members for universe {name} are: {members}.")

    @universes.command()
    @click.option("-n", "--name", "name", required=True, type=str)
    @click.confirmation_option(prompt="Are you sure you want to delete this universe?")
    def delete(self, name):
        """Delete universe"""
        self.app.delete_universe(universe=name)
        click.echo(f"Deleted universe {name}.")


if __name__ == '__main__':
    """Docstring"""

    # Setup logging
    FORMAT = "%(message)s"
    logging.basicConfig(format=FORMAT, level=logging.INFO)

    cli = CommandLineInterface()
    cli.cli()
