import sqlite3
import pandas as pd

from barbucket.database import DataBase


class UniversesDB(DataBase):

    def __init__(self):
        """

        """



    def __create_membership(self, contract_id, universe):
        # Todo: Return success or not

        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""INSERT INTO universe_memberships (contract_id, universe) 
            VALUES (?, ?)""", (contract_id, universe))

        conn.commit()
        cur.close()
        self.disconnect(conn)



    def create_universe_conditional(self, name, conditions={}):
        if conditions == {}:
                print(f"Error. No conditions given.")
                return

        # Check if given condition fields are valid
        query = """SELECT name FROM PRAGMA_TABLE_INFO("universe_memberships");"""

        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(query)
        result = cur.fetchall()

        conn.commit()
        cur.close()
        self.disconnect(conn)

        existing_columns = []
        for row in result:
            existing_columns.append(row['name'])

        for key in conditions:
            if key not in existing_columns:
                print(f"Error. Condition key '{key}' not found in columns.")
                return

        # Prepare query to get requested values from db
        query = 'SELECT contract_id FROM all_contract_info'
        query += ' WHERE '

        for key, value in conditions.items():
            query += (key + " = '" + str(value) + "' and ")

        query = query[:-5]      #remove trailing 'and'

        # Get requested values from db
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute(query)
        result = cur.fetchall()

        conn.commit()
        cur.close()
        self.disconnect(conn)

        if len(result) == 0:
            print(f"Error. No contracts matched conditions.")
            return

        # Insert memberships into db
        for contract in result:
            self.__create_membership(contract['contract_id'], name)

        print(f"Successfully created universe '{name}' with {len(result)} members.")



    def create_universe(self, name, contract_ids):
        # Insert memberships into db
        for contract_id in contract_ids:
            self.__create_membership(contract_id, name)

        print(f"Successfully created universe '{name}' with {len(contract_ids)} members.")



    def get_universes(self):
        """
        returns a list of sqlite3.Row objects ???
        """

        query = f"SELECT DISTINCT universe \
            FROM universe_memberships;"

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
            result.append(row["universe"])

        return result



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