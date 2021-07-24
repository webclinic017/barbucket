import click

from barbucket.app_interface import AppInterface


app = AppInterface()


# Initial group, not explicitly called
@click.group()
def cli():
    pass


# Group database
@cli.group()
def database():
    """Local database commands"""

@database.command()
@click.confirmation_option(prompt="Are you sure you want to archive the database?")
def archive():
    """Archive the local database"""
    app.archive_database()
    click.echo("Archived database.")


# Group contracts
@cli.group()
def contracts():
    """Contracts commands"""

@contracts.command()
@click.option("-t", "--type", "contract_type", required=True, type=str)
@click.option("-e", "--exchange", "exchange", required=True, type=str)
def sync_listing(contract_type, exchange):
    """Sync master listing to IB exchange listing"""
    app.sync_contracts_to_listing(ctype=contract_type.upper(), exchange=exchange.upper())
    click.echo(f"Master listing synced for {contract_type.upper()} on {exchange.upper()}.")

@contracts.command()
def fetch_ib_details():
    """Fetch details for all contracts from IB TWS"""
    app.fetch_ib_contract_details()
    click.echo("Updated IB details for master listings.")

@contracts.command()
def fetch_tv_details():
    """Fetch details for all contracts from TV files"""
    app.ingest_tv_files()
    click.echo(f"Finished ingesting TV files.")


# Group quotes
@cli.group()
def quotes():
    """Quotes commands"""

@quotes.command()
@click.option("-u", "--universe", "universe", required=True, type=str)
def fetch(universe):
    """Fetch quotes from IB TWS"""
    app.fetch_historical_quotes(universe=universe)
    click.echo(f"Finished collecting historical data for universe: {universe}")


# Group universes
@cli.group()
def universes():
    """Universes commands"""

@universes.command()
@click.option("-n", "--name", "name", required=True, type=str)
@click.option("-c", "--contract_ids", "contract_ids", required=True, type=str)
def create(name, contract_ids):
    """Create new universe"""
    con_list = [int(n) for n in contract_ids.split(",")]
    app.create_universe(name=name, contract_ids=con_list)
    click.echo(f"Created universe {name}.")

@universes.command()
def list():
    """List all universes"""
    result = app.get_universes()
    click.echo(f"Existing universes: {result}.")

@universes.command()
@click.option("-n", "--name", "name", required=True, type=str)
def members(name):
    """List universes members"""
    members = app.get_universe_members(universe=name)
    click.echo(f"Members for universe {name} are: {members}.")

@universes.command()
@click.option("-n", "--name", "name", required=True, type=str)
@click.confirmation_option(prompt="Are you sure you want to delete this universe?")
def delete(name):
    """Delete universe"""
    app.delete_universe(universe=name)
    click.echo(f"Deleted universe {name}.")



if __name__ == '__main__':
    cli()
