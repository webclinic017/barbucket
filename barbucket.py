import fire

from barbucket.contracts_db import ContractsDB
from barbucket.contract_details_db import ContractTwDetailsDB
from barbucket.quotes_db import QuotesDB
from barbucket.universes_db import UniversesDB
from barbucket.tws_connector import TwsConnector
from barbucket.data_quality_check import DataQualityCheck

cont_db = ContractsDB()
details_db = ContractTwDetailsDB()
quot_db = QuotesDB()
univ_db = UniversesDB()
tws_conn = TwsConnector()
dq_check = DataQualityCheck()


# Template
# class MyGroup(object):
#     def my_command(self, my_argument_1, my_argument_2):
        # Call code functions here


# Playground
class Playground(object):
    # python barbucket.py playground listreader --my_list "[a,b]"
    def listreader(self, my_list):
        """
        First line
        Second line
        :param my_list Parameter 1
        :raises SomeError Description
        :returns Some Text
        """
        for elem in my_list:
            print(elem)


class Database(object):
    # python barbucket.py database init
    def init(self):
        print("You sure? (y/n): ", end="")
        if input().lower() == "y":
            cont_db.init_database()
            print("Initialized databse.")
        else:
            print("Aborted")


class Contracts(object):
    # python barbucket.py contracts sync_listing --contract_type stock
    #   --exchanges island/arca/nyse
    def sync_listing(self, contract_type, exchange):
        cont_db.sync_contracts_to_listing(ctype=contract_type, exchange=exchange)
        print(f"Finished for {contract_type} on {exchange}.")

    # python barbucket.py contracts ingest_tw_files
    def ingest_tw_files(self):
        details_db.ingest_tw_files()
        print(f"Finished ingesting files.")


class Universes(object):
    # python barbucket.py universes create --name my_univ
    #   --contract_ids [22,33,789]
    def create(self, name, contract_ids):
        univ_db.create_universe(name, contract_ids)
        print(f"Created universe {name}.")


class TwsConnector(object):
    # python barbucket.py tws get_histo_data --universe russell3000
    def get_histo_data(self, universe):
        tws_conn.get_historical_data(universe)
        print(f"Finished collecting historical data for universe: {universe}")


class Cli(object):
    def __init__(self):
        # self.my_group = MyGroup()     # Template
        self.playground = Playground()
        self.database = Database()
        self.contracts = Contracts()
        self.universes = Universes()
        self.tws = TwsConnector()


if __name__ == '__main__':
  fire.Fire(Cli)

# Old code
# tws_conn.get_historical_data()
# dq_check.handle_single_contract(contract_id=108)
# dq_check.get_trading_calendar("FWB")