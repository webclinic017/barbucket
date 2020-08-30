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


    def get_universes(self):
        pass


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