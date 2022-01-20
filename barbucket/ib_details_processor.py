import logging
from typing import Any, List

import enlighten
from ib_insync.wrapper import RequestError
import sqlite3

from .signal_handler import SignalHandler, ExitSignalDetectedError
from .tws_connector import TwsConnector, IbDetailsInvalidError
from .db_connector import DbConnector

logger = logging.getLogger(__name__)


class IbDetailsProcessor():
    """Downloading of contract details from IB TWS and storing to db"""

    def __init__(self) -> None:
        self.__tws_connector = TwsConnector()
        self.__db_connector = DbConnector()
        self.__contracts: List[Any] = []
        self.__details: Any = None
        self.__pbar: Any = None
        self.__signal_handler = SignalHandler()
        manager = enlighten.get_manager()  # Setup progress bar
        self.__pbar = manager.counter(
            total=0,
            desc="Contracts", unit="contracts")

    def update_ib_contract_details(self) -> None:
        """Download and store all missing contract details entries from IB TWS.
        """

        self.__get_contracts()
        self.__pbar.total = len(self.__contracts)
        self.__tws_connector.connect()
        try:
            for contract in self.__contracts:
                self.__signal_handler.is_exit_requested()
                logger.info(
                    f"{contract['broker_symbol']}_{contract['exchange']}_"
                    f"{contract['currency']}")
                try:
                    self.__get_contract_details_from_tws(contract)
                except RequestError as e:
                    logger.info(e)
                    continue
                except IbDetailsInvalidError as e:
                    logger.info(e)
                    continue
                else:
                    self.__insert_ib_details_into_db(contract)
                finally:
                    self.__pbar.update(inc=1)
        except ExitSignalDetectedError:
            pass
        else:
            logger.info(
                f"Updated IB details for master listings.")
        finally:
            self.__tws_connector.disconnect()

    def __get_contracts(self) -> None:
        """Get contracts from db, where IB details are missing"""

        query = """
            SELECT contract_id, broker_symbol, exchange, currency 
                FROM all_contract_info
                WHERE primary_exchange IS NULL"""

        conn = self.__db_connector.connect()
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query)
        self.__contracts = cur.fetchall()
        conn.commit()
        cur.close()
        self.__db_connector.disconnect(conn)
        logger.info(f"Found {len(self.__contracts)} contracts with missing "
                    f"IB details in master listing.")

    def __get_contract_details_from_tws(self, contract: Any) -> None:
        self.__details = self.__tws_connector.download_contract_details(
            broker_symbol=contract['broker_symbol'],
            exchange=contract['exchange'],
            currency=contract['currency'])

    def __insert_ib_details_into_db(self, contract: Any) -> None:
        contract_id = contract['contract_id'],
        contract_type_from_details = self.__details.stockType,
        primary_exchange = self.__details.contract.primaryExchange,
        industry = self.__details.industry,
        category = self.__details.category,
        subcategory = self.__details.subcategory

        conn = self.__db_connector.connect()
        cur = conn.cursor()
        cur.execute("""
            REPLACE INTO contract_details_ib (
                contract_id,
                contract_type_from_details,
                primary_exchange,
                industry,
                category,
                subcategory)
                VALUES (?, ?, ?, ?, ?, ?)""", (
                    contract_id,
                    contract_type_from_details,
                    primary_exchange,
                    industry,
                    category,
                    subcategory))
        conn.commit()
        cur.close()
        self.__db_connector.disconnect(conn)
        logger.debug(f"Inserted IB details into db: {contract_id} "
                     f"{contract_type_from_details} {primary_exchange} "
                     f"{industry} {category} {subcategory}")
