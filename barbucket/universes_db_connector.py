import sqlite3
import logging
from typing import List

from .db_connector import DbConnector

logger = logging.getLogger(__name__)


class UniversesDbConnector(DbConnector):

    def __init__(self) -> None:
        super().__init__()

    def create_universe(self, name: str, contract_ids: List[int]) -> None:
        """Create a new universe with given contracts

        :param name: New universes name
        :type name: str
        :param contract_ids: Contract IDs of universes members
        :type contract_ids: List[int]
        """

        for contract_id in contract_ids:
            self.__create_membership(contract_id, name)
        logger.debug(
            f"Created universe '{name}' with {len(contract_ids)} contracts.")

    def __create_membership(self, contract_id: int, universe: str) -> None:
        # Todo: What if member does not exist?

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO universe_memberships (contract_id, universe) 
                VALUES (?, ?)""",
            (contract_id, universe))
        conn.commit()
        cur.close()
        self.disconnect(conn)
        logger.debug(
            f"Created universe membership for {contract_id} in universe "
            f"'{universe}'")

    def get_universes(self) -> List[str]:
        """Get all existing universes

        :return: All existing universes
        :rtype: List[str]
        """

        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT universe FROM universe_memberships;")
        row_list = cur.fetchall()
        conn.commit()
        cur.close()
        self.disconnect(conn)
        logger.debug(f"Query for universes returned {len(row_list)} entries")
        return [row['universe'] for row in row_list]

    def get_universe_members(self, universe: str) -> List[int]:
        """Get all members of a given universe

        :param universe: Name of the universe
        :type universe: str
        :return: Members of the universe
        :rtype: List[int]
        """

        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            """SELECT contract_id 
                FROM universe_memberships 
                WHERE universe = ?;""",
            (universe,))  # Comma, to not iterate over string characters
        row_list = cur.fetchall()
        conn.commit()
        cur.close()
        self.disconnect(conn)
        logger.debug(
            f"Query for members of universe '{universe}' returned {len(row_list)} "
            f"entries")
        return [row['contract_id'] for row in row_list]

    def delete_universe(self, universe: str) -> int:
        """Delete an existing universe

        :param universe: Name of the universe
        :type universe: str
        :return: Number of members
        :rtype: int
        """

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM universe_memberships WHERE universe = ?;",
            (universe,))  # tuple, to not iterate over string characters
        cur.execute(
            "select changes()")
        n_affeced_rows = cur.fetchone()[0]
        conn.commit()
        cur.close()
        self.disconnect(conn)
        logger.debug(
            f"Deleting universe '{universe}' resulted in {n_affeced_rows} "
            f"affected rows")
        return n_affeced_rows
