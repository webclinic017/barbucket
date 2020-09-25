from barbucket.database import Database
from barbucket.contracts import Contracts
from barbucket.tv_details import TvDetails
from barbucket.quotes import Quotes
from barbucket.universes import UniversesDatabase


class AppInterface():

    def __init__(self):
        pass


    def reset_database(self,):
        database = Database()
        database.init_database()


    def get_contracts(self, filters, return_columns):
        contracts = Contracts()
        contracts = contracts.get_contracts(filters=filters,
            return_columns=return_columns)
        return contracts


    def sync_contracts_to_listing(self, type, exchange):
        contracts = Contracts()
        contracts.sync_contracts_to_listing(ctype=type, exchange=exchange)


    def ingest_tw_files(self,):
        tv_details = TvDetails()
        tv_details.ingest_tw_files()


    def fetch_historical_quotes(self, universe):
        quotes = Quotes()
        quotes.fetch_historical_quotes(universe=universe)


    def get_quotes(self, contract_id):
        quotes = Quotes()
        result = quotes.get_contract_quotes(contract_id)
        return result


    def create_universe(self, name, contract_ids):
        universes = UniversesDatabase()
        universes.create_universe(name=name, contract_ids=contract_ids)


    def get_universes(self,):
        universes = UniversesDatabase()
        universes.get_universes()


    def get_universe_members(self, universe):
        universes = UniversesDatabase()
        universes.get_universe_members(universe)


    def delete_universe(self, universe):
        universes = UniversesDatabase()
        universes.delete_universe(universe)
