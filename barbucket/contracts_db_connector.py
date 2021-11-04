import sqlite3
import logging
from typing import Dict, List

from .db_connector import DbConnector

logger = logging.getLogger(__name__)


class ContractsDbConnector(DbConnector):
    """Provides methods to access the 'contracts' table of the database."""

    def __init__(self) -> None:
        super().__init__()

    def create_contract(self, contract_type_from_listing: str,
                        exchange_symbol: str, broker_symbol: str, name: str,
                        currency: str, exchange: str) -> None:
        """Creates a new contract in the database

        :param contract_type_from_listing: Type of contract from the listing
        :type contract_type_from_listing: str
        :param exchange_symbol: Contract symbol at exchange
        :type exchange_symbol: str
        :param broker_symbol: Contract symbol at broker
        :type broker_symbol: str
        :param name: Contract name
        :type name: str
        :param currency: Contract currency
        :type currency: str
        :param exchange: Contract exchange
        :type exchange: str
        """
        # Todo: what if already exits?

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO contracts (
                    contract_type_from_listing,
                    exchange_symbol,
                    broker_symbol,
                    name,
                    currency,
                    exchange)
                    VALUES (?, ?, ?, ?, ?, ?)""",
            (contract_type_from_listing,
                exchange_symbol,
                broker_symbol,
                name,
                currency,
                exchange))
        conn.commit()
        cur.close()
        self.disconnect(conn)
        logger.debug(
            f"Created new contract_db entry: {contract_type_from_listing}_"
            f"{exchange}_{broker_symbol}_{currency}.")

    def get_contracts(self, filters: Dict = {}, return_columns: List = []
                      ) -> List[sqlite3.Row]:
        """Returns the requsted columns of the contracts table, filtered by 
        the given filters

        :param filters: Equality conditions for filtering, formatted as a 
        dictionary: {'column_name': "value"}. Value can be int, float or 
        string, defaults to {}
        :type filters: Dict, optional
        :param return_columns: List of column names to return, empty list 
        returns all columns, defaults to []
        :type return_columns: List, optional
        :return: List of rows matching the given parameters
        :rtype: List[sqlite3.Row]
        """

        # Prepare query
        query = "SELECT * FROM all_contract_info"
        if len(return_columns) > 0:
            cols = ", ".join(return_columns)
            query = query.replace("*", cols)
        if len(filters) > 0:
            query += " WHERE "
            for key, value in filters.items():
                if value == "NULL":
                    query += (key + " IS " + str(value) + " and ")
                elif isinstance(value, str):
                    query += (key + " = '" + str(value) + "' and ")
                elif isinstance(value, (int, float)):
                    query += (key + " = " + str(value) + " and ")
            query = query[:-5]  # remove trailing 'and'
            query += ";"

        # Get requested values from db
        conn = self.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query)
        contracts = cur.fetchall()
        conn.commit()
        cur.close()
        self.disconnect(conn)
        logger.debug(f"Qurey '{query}' returned {len(contracts)} results.")
        return contracts

    def delete_contract(self, exchange: str, symbol: str, currency: str) -> None:
        """Deletets a contract from the db.

        :param exchange: Exchange of the contract to delete
        :type exchange: str
        :param symbol: Symbol of the contract to delete
        :type symbol: str
        :param currency: Currency of the contract to delete
        :type currency: str
        """

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            """DELETE FROM contracts
                    WHERE (broker_symbol = ?
                        AND exchange = ?
                        AND currency = ?);""",
            (symbol, exchange, currency))
        conn.commit()
        cur.close()
        self.disconnect(conn)
        logger.debug(f"Deleted contract: {exchange}_{symbol}_{currency}")

    def delete_contract_id(self, contract_id: int) -> None:
        """Deletets a contract from the db.

        :param contract_id: Contract ID of the contract to delete
        :type contract_id: int
        """

        conn = self.connect()
        cur = conn.cursor()
        cur.execute(
            """DELETE FROM contracts
                    WHERE contract_id = ?;""",
            (contract_id,))
        conn.commit()
        cur.close()
        self.disconnect(conn)
        logger.debug(f"Deleted contract with id {contract_id}")
