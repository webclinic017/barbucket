import fire

from barbucket.app_interface import AppInterface



app = AppInterface()


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
    # python barbucket.py database reset
    def reset(self):
        print("You sure? (y/n): ", end="")
        if input().lower() == "y":
            app.reset_database()
            print("Initialized databse.")
        else:
            print("Aborted")


class Contracts(object):
    # python barbucket.py contracts sync_listing --contract_type stock
    #   --exchange island/arca/nyse
    def sync_listing(self, contract_type, exchange):
        app.sync_contracts_to_listing(ctype=contract_type, exchange=exchange)
        print(f"Master listing synced for {contract_type}s on {exchange}.")


class TvDetails(object):
    # python barbucket.py tvdetails ingest_files
    def ingest_tv_files(self):
        app.ingest_tw_files()
        print(f"Finished ingesting TV files.")


class Quotes(object):
    # python barbucket.py quotes fetch --universe my_universe
    def fetch(self, universe):
        app.fetch_historical_quotes(universe=universe)
        print(f"Finished collecting historical data for universe: {universe}")


class Universes(object):
    # python barbucket.py universes create --universe my_univ
    #   --contract_ids [22,33,789]
    def create(self, universe, contract_ids):
        app.create_universe(universe, contract_ids)
        print(f"Created universe {universe}.")

    # python barbucket.py universes list
    def list(self,):
        universes = app.get_universes()
        print(f"Existing universes: {universes}.")

    # python barbucket.py universes members --name my_univ
    def members(self, universe):
        members = app.get_universe_members(universe=universe)
        print(f"Members for universe {universe} are: {members}.")

    # python barbucket.py universes delete --name my_univ
    def delete(self, universe):
        app.delete_universe(universe)
        print(f"Deleted universe {universe}.")


class Cli(object):
    def __init__(self):
        # self.my_group = MyGroup()     # Template
        self.playground = Playground()
        self.database = Database()
        self.contracts = Contracts()
        self.tv_details = TvDetails()
        self.quotes = Quotes()
        self.universes = Universes()


if __name__ == '__main__':
  fire.Fire(Cli)
