import sqlite3

from barbucket.database import DatabaseConnector


class UniversesDatabase():

    def __init__(self):
        pass


    def __create_membership(self, contract_id, universe):
        # Todo: Return success or not

        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        cur = conn.cursor()

        cur.execute("""INSERT INTO universe_memberships (contract_id, universe) 
            VALUES (?, ?)""", (contract_id, universe))

        conn.commit()
        cur.close()
        db_connector.disconnect(conn)


    # def create_universe_conditional(self, name, conditions={}):
    #     if conditions == {}:
    #             print(f"Error. No conditions given.")
    #             return

    #     # Check if given condition fields are valid
    #     query = """SELECT name FROM PRAGMA_TABLE_INFO("universe_memberships");"""

    #     db_connector = DatabaseConnector()
    #     conn = db_connector.connect()
    #     conn.row_factory = sqlite3.Row
    #     cur = conn.cursor()

    #     cur.execute(query)
    #     result = cur.fetchall()

    #     conn.commit()
    #     cur.close()
    #     db_connector.disconnect(conn)

    #     existing_columns = []
    #     for row in result:
    #         existing_columns.append(row['name'])

    #     for key in conditions:
    #         if key not in existing_columns:
    #             print(f"Error. Condition key '{key}' not found in columns.")
    #             return

    #     # Prepare query to get requested values from db
    #     query = 'SELECT contract_id FROM all_contract_info'
    #     query += ' WHERE '

    #     for key, value in conditions.items():
    #         query += (key + " = '" + str(value) + "' and ")

    #     query = query[:-5]      #remove trailing 'and'

    #     # Get requested values from db
    #     conn = db_connector.connect()
    #     conn.row_factory = sqlite3.Row
    #     cur = conn.cursor()

    #     cur.execute(query)
    #     result = cur.fetchall()

    #     conn.commit()
    #     cur.close()
    #     db_connector.disconnect(conn)

    #     if len(result) == 0:
    #         print(f"Error. No contracts matched conditions.")
    #         return

    #     # Insert memberships into db
    #     for contract in result:
    #         self.__create_membership(contract['contract_id'], name)

    #     print(f"Successfully created universe '{name}' with {len(result)} members.")


    def create_universe(self, name, contract_ids):
        # Todo: If number of contracts < 1 abort

        # Insert memberships into db
        for contract_id in contract_ids:
            self.__create_membership(contract_id, name)

        print(f"Successfully created universe '{name}' with {len(contract_ids)} members.")


    def get_universes(self):
        """
        returns a list of strings
        """

        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT DISTINCT universe FROM universe_memberships;")
        row_list = cur.fetchall()

        conn.commit()
        cur.close()
        db_connector.disconnect(conn)

        result = []
        for row in row_list:
            result.append(row['universe'])

        return result


    def get_universe_members(self, universe):
        """
        returns a list of contract_ids
        """

        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""SELECT contract_id 
            FROM universe_memberships 
            WHERE universe = ?;""", (universe,))
        row_list = cur.fetchall()

        conn.commit()
        cur.close()
        db_connector.disconnect(conn)

        result = []
        for row in row_list:
            result.append(row['contract_id'])

        return result


    def delete_universe(self, universe):

        db_connector = DatabaseConnector()
        conn = db_connector.connect()
        cur = conn.cursor()

        cur.execute("DELETE FROM universe_memberships WHERE universe = ?;",
            (universe,))

        conn.commit()
        cur.close()
        db_connector.disconnect(conn)