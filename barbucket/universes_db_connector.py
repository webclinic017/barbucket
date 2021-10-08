import sqlite3
import logging
from typing import List

from .mediator import Mediator
from .db_connector import DbConnector

logger = logging.getLogger(__name__)


class UniversesDbConnector(DbConnector):

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator

    def create_universe(self, name: str, contract_ids: List[int]) -> None:
        """Create a new universe with given contracts"""

        for contract_id in contract_ids:
            self.__create_membership(contract_id, name)
        logger.debug(f"Created universe '{name}' with {len(contract_ids)}"
                     f" contracts.")

    def __create_membership(self, contract_id: int, universe: str) -> None:
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("""INSERT INTO universe_memberships (contract_id, universe) 
            VALUES (?, ?)""", (contract_id, universe))
        conn.commit()
        cur.close()
        self.disconnect(conn)

    def get_universes(self) -> List[str]:
        """Get all existing universes"""

        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT universe FROM universe_memberships;")
        row_list = cur.fetchall()
        conn.commit()
        cur.close()
        self.disconnect(conn)

        result = []
        for row in row_list:
            result.append(row['universe'])
        return result

    def get_universe_members(self, universe: str) -> List[int]:
        """Get all members of a given universe"""

        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""SELECT contract_id 
            FROM universe_memberships 
            WHERE universe = ?;""", (universe,))
        row_list = cur.fetchall()
        conn.commit()
        cur.close()
        self.disconnect(conn)

        result = []
        for row in row_list:
            result.append(row['contract_id'])
        return result

    def delete_universe(self, universe: str) -> None:
        """Delete an existing universe"""

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM universe_memberships WHERE universe = ?;",
            (universe,))
        conn.commit()
        cur.close()
        self.disconnect(conn)
        logger.debug(f"Deleted universe '{universe}'.")
