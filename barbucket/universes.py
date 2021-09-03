import sqlite3
import logging

from .mediator import Mediator


class UniversesDatabase():

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator

    def __create_membership(self, contract_id, universe):
        conn = self.mediator.notify("get_db_connection", {})
        cur = conn.cursor()

        cur.execute("""INSERT INTO universe_memberships (contract_id, universe) 
            VALUES (?, ?)""", (contract_id, universe))

        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})

    def create_universe(self, name, contract_ids):

        # Insert memberships into db
        logging.info(
            f"Creating universe '{name}' with {len(contract_ids)} members.")
        for contract_id in contract_ids:
            self.__create_membership(contract_id, name)

    def get_universes(self):
        """
        returns a list of strings
        """

        conn = self.mediator.notify("get_db_connection", {})
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("SELECT DISTINCT universe FROM universe_memberships;")
        row_list = cur.fetchall()

        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})

        result = []
        for row in row_list:
            result.append(row['universe'])

        return result

    def get_universe_members(self, universe):
        """
        returns a list of contract_ids
        """

        conn = self.mediator.notify("get_db_connection", {})
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""SELECT contract_id 
            FROM universe_memberships 
            WHERE universe = ?;""", (universe,))
        row_list = cur.fetchall()

        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})

        result = []
        for row in row_list:
            result.append(row['contract_id'])

        return result

    def delete_universe(self, universe):

        logging.info(f"Deleting universe '{universe}'.")
        conn = self.mediator.notify("get_db_connection", {})
        cur = conn.cursor()

        cur.execute(
            "DELETE FROM universe_memberships WHERE universe = ?;",
            (universe,))

        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})
