import fire

from barbucket.contracts_db import ContractsDB
from barbucket.quotes_db import QuotesDB
from barbucket.tws_connector import TwsConnector
from barbucket.data_quality_check import DataQualityCheck

cont_db = ContractsDB()
quot_db = QuotesDB()
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
    #   --exchanges "[nasdaq,nyse,arca,amex]"
    def sync_listing(self, contract_type, exchanges):
        for ex in exchanges:
            cont_db.sync_contracts_to_listing(ctype=contract_type, exchange=ex)
            print(f"Finished for {contract_type} on {ex}.")


class TwsConnector(object):
    def req_data(self):
        tws_conn.get_historical_data()
        print(f"Finished")


class Cli(object):
    def __init__(self):
        # self.my_group = MyGroup()     # Template
        self.playground = Playground()
        self.database = Database()
        self.contracts = Contracts()
        self.tws = TwsConnector()


if __name__ == '__main__':
  fire.Fire(Cli)

# Old code
# tws_conn.get_historical_data()
# dq_check.handle_single_contract(contract_id=108)
# dq_check.get_trading_calendar("FWB")