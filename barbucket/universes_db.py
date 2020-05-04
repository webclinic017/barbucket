import sqlite3
import pandas as pd

from barbucket.database import DataBase
from barbucket.contracts_db import ContractsDB


class UniversesDB(DataBase):

    def __init__(self):
        """

        """
        self.__contracts_db = ContractsDB()


    def __create_membership(self, contract_id, universe):
        # Todo: Return success or not

        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""INSERT INTO universe_memberships (contract_id, universe) 
            VALUES (?, ?)""", (contract_id, universe))

        conn.commit()
        cur.close()
        self.disconnect(conn)


    def get_universe_members(self, universe):
        """
        returns a list of sqlite3.Row objects ???
        """

        query = f'SELECT contract_id \
            FROM universe_memberships \
            WHERE universe = "{universe}";'

        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(query)
        row_list = cur.fetchall()

        conn.commit()
        cur.close()
        self.disconnect(conn)

        result = []
        for row in row_list:
            result.append(row["contract_id"])

        return result


    def delete_universe(self, universe):

        query = f'DELETE FROM universe_memberships \
                    WHERE (universe = "{universe}");'
        
        conn = self.connect()
        cur = conn.cursor()

        cur.execute(query)

        conn.commit()
        cur.close()
        self.disconnect(conn)


    def update_russell3000(self):

        self.delete_universe("russell3000")
        
        exchange_map = {
            "NASDAQ": "nasdaq",
            "New York Stock Exchange Inc.": "nyse",
            "Cboe BZX formerly known as BATS": "nyse",
            "Nyse Mkt Llc": "nyse"
        }

        file_url = "https://www.ishares.com/us/products/239714/ishares-russell-3000-etf/1467271812596.ajax?fileType=csv&fileName=IWV_holdings&dataType=fund"
        file_path = "IWV_holdings.csv"
        listing = pd.read_csv(file_path, header=9)
        contracts_not_found = 0
        contracts_with_multi_results = 0
        contracts_added = 0

        for _, row in listing.iterrows():
            
            if row["Exchange"] in exchange_map.keys():
                matches = self.__contracts_db.get_contracts(
                    ctype="stock",
                    exchange_symbol=row["Ticker"],
                    exchange=exchange_map[row["Exchange"]])
                if len(matches) == 0:
                    contracts_not_found += 1
                elif len(matches) > 1:
                    contracts_with_multi_results += 1
                else:
                    self.__create_membership(
                        contract_id=matches[0]["contract_id"],
                        universe="russell3000")
                    contracts_added += 1

            else:
                contracts_not_found += 1

        print(f"Length of listing: {len(listing)}")
        print(f"Contracts not found: {contracts_not_found + contracts_with_multi_results}")
        print(f"Contracts added to universe: {contracts_added}")


    def update_universe(self, universe):
        if universe.lower() == "russell3000":
            self.update_russell3000()