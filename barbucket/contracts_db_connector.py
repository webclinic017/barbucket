import sqlite3
import logging
from typing import Dict, List

from .mediator import Mediator

logger = logging.getLogger(__name__)


class ContractsDbConnector():
    """Provides methods to access the 'contracts' table of the database."""

    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator

    def create_contract(self, contract_type_from_listing: str,
                        exchange_symbol: str, broker_symbol: str, name: str,
                        currency: str, exchange: str) -> None:
        """Creates a new contract in the database."""

        contract_id = self.__create_contracts_db_entry(
            contract_type_from_listing,
            exchange_symbol,
            broker_symbol,
            name,
            currency,
            exchange)
        self.__create_contracts_status_db_entry(contract_id)
        logger.info(f"Created new contract {contract_type_from_listing}_"
                    f"{exchange}_{broker_symbol}_{currency}.")

    def __create_contracts_db_entry(self, contract_type_from_listing: str,
                                    exchange_symbol: str, broker_symbol: str,
                                    name: str, currency: str, exchange: str
                                    ) -> int:
        """Creates a new entry in the contracts table."""

        conn = self.mediator.notify("get_db_connection")
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
        contract_id = cur.lastrowid()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})
        return contract_id

    def __create_contracts_status_db_entry(self, contract_id: int) -> None:
        """Creates a new entry in the contracts_status table."""

        conn = self.mediator.notify("get_db_connection")
        cur = conn.cursor()
        self.mediator.notify(
            "insert_quotes_status",
            {'contract_id': contract_id,
             'status_code': 0,
             'status_text': "NULL",
             'daily_quotes_requested_from': "NULL",
             'daily_quotes_requested_till': "NULL"})
        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})

    def get_contracts(self, filters: Dict = {}, return_columns: List = []
                      ) -> List[sqlite3.Row]:
        """
        Returns the requsted columns of the contracts table, filtered by the
        given filters
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
        logger.info(f"Getting contracts from databse with query: {query}")
        conn = self.mediator.notify("get_db_connection")
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query)
        contracts = cur.fetchall()
        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})
        logger.info(f"Qurey '{query}' returned {len(contracts)} results.")
        return contracts

    def delete_contract(self, exchange: str, symbol: str, currency: str) -> None:
        """Deletets a contract from the db."""

        conn = self.mediator.notify("get_db_connection")
        cur = conn.cursor()
        cur.execute(
            """DELETE FROM contracts
                    WHERE (broker_symbol = ?
                        AND exchange = ?
                        AND currency = ?);""",
            (symbol, exchange, currency))
        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})
        logger.info(f"Deleted contract: {exchange}_{symbol}_{currency}")

    def delete_contract_id(self, contract_id: int) -> None:
        """Deletets a contract from the db."""

        conn = self.mediator.notify("get_db_connection")
        cur = conn.cursor()
        cur.execute(
            """DELETE FROM contracts
                    WHERE contract_id = ?;""",
            contract_id)
        conn.commit()
        cur.close()
        self.mediator.notify("close_db_connection", {'conn': conn})
        logger.info(f"Deleted contract with id {contract_id}")
