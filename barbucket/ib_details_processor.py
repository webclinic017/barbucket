import logging
from typing import Any, List

import enlighten
from ib_insync.wrapper import RequestError

from .signal_handler import SignalHandler, ExitSignalDetectedError
from .contracts_db_connector import ContractsDbConnector
from .ib_details_db_connector import IbDetailsDbConnector
from .tws_connector import TwsConnector

logger = logging.getLogger(__name__)


class IbDetailsProcessor():
    """Downloading of contract details from IB TWS and storing to db"""

    def __init__(self) -> None:
        self.__contracts_db_connector = ContractsDbConnector()
        self.__ib_details_db_connector = IbDetailsDbConnector()
        self.__tws_connector = TwsConnector()
        self.__contracts: List[Any] = None
        self.__details: Any = None
        self.__pbar: Any = None
        self.__signal_handler = SignalHandler()
        manager = enlighten.get_manager()  # Setup progress bar
        self.__pbar = manager.counter(
            total=0,
            desc="Contracts", unit="contracts")

    def update_ib_contract_details(self) -> None:
        """Download and store all missing contract details entries from IB TWS."""

        self.__get_contracts()
        self.__pbar.total = len(self.__contracts)
        self.__connect_tws()
        try:
            for contract in self.__contracts:
                if self.__signal_handler.exit_requested():
                    raise ExitSignalDetectedError("Message")
                logger.info(
                    f"{contract['broker_symbol']}_{contract['exchange']}_"
                    f"{contract['currency']}")
                try:
                    self.__get_contract_details_from_tws(contract)
                except RequestError as e:
                    logger.info(e)
                    continue
                if not self.__details_valid():
                    self.__pbar.update(inc=1)
                    continue
                else:
                    self.__decode_exchange_names()
                    self.__insert_ib_details_into_db(contract)
                    self.__pbar.update(inc=1)
        except ExitSignalDetectedError:
            pass
        else:
            logger.info(
                f"Updated IB details for master listings.")
        finally:
            self.__disconnect_tws()

    def __get_contracts(self) -> None:
        """Get contracts from db, where IB details are missing"""

        return_columns = [
            'contract_id', 'contract_type_from_listing', 'broker_symbol',
            'exchange', 'currency']
        filters = {'primary_exchange': "NULL"}
        self.__contracts = self.__contracts_db_connector.get_contracts(
            filters=filters,
            return_columns=return_columns)
        logger.info(f"Found {len(self.__contracts)} contracts with missing "
                    f"IB details in master listing.")

    def __connect_tws(self) -> None:
        """Connect to TWS app"""
        self.__tws_connector.connect()

    def __disconnect_tws(self) -> None:
        """Disconnect from TWS app"""
        self.__tws_connector.disconnect()

    def __get_contract_details_from_tws(self, contract: Any) -> None:
        """Download contract details over TWS."""

        self.__details = self.__tws_connector.download_contract_details(
            broker_symbol=contract['broker_symbol'],
            exchange=contract['exchange'],
            currency=contract['currency'])

    def __details_valid(self) -> bool:
        if self.__details is None:
            logger.info(f"Result is None")
            return False
        elif len(self.__details) == 0:
            logger.info(f"Result is []")
            return False
        elif len(self.__details) > 1:
            logger.info(f"Multiple results")
            return False
        else:
            self.__details = self.__details[0]
            return True

    def __decode_exchange_names(self) -> None:
        """Decode exchange names"""
        self.__details.contract.exchange = Exchange.decode(
            name=self.__details.contract.exchange,
            from_api=Api.IB)
        self.__details.contract.primaryExchange = Exchange.decode(
            name=self.__details.contract.primaryExchange,
            from_api=Api.IB)

    def __insert_ib_details_into_db(self, contract: Any) -> None:
        """Insert contract details into db"""

        self.__ib_details_db_connector.insert_ib_details(
            contract_id=contract['contract_id'],
            contract_type_from_details=self.__details.stockType,
            primary_exchange=self.__details.contract.primaryExchange,
            industry=self.__details.industry,
            category=self.__details.category,
            subcategory=self.__details.subcategory)
