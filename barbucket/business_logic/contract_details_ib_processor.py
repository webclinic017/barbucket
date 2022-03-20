import logging

from sqlalchemy.orm import Session
import enlighten
from ib_insync.wrapper import RequestError

from barbucket.api.tws_connector import TwsConnector
from barbucket.persistence.data_managers import ContractDetailsIbDbManager, ContractsDbManager
from barbucket.domain_model.data_classes import Contract
from barbucket.util.custom_exceptions import InvalidDataReceivedError
from barbucket.util.signal_handler import SignalHandler


_logger = logging.getLogger(__name__)


class ContractDetailsIbProcessor():

    def __init__(self,
                 tws_connector: TwsConnector,
                 details_db_manager: ContractDetailsIbDbManager,
                 contracts_db_manager: ContractsDbManager,
                 orm_session: Session) -> None:
        self._tws_connector = tws_connector
        self._details_db_manager = details_db_manager
        self._contracts_db_manager = contracts_db_manager
        self._orm_session = orm_session

    def update_ib_contract_details(self) -> None:
        signal_handler = SignalHandler()
        pb_manager = enlighten.get_manager()  # Setup progress bar
        progress_bar = pb_manager.counter(
            total=0, desc="Contracts", unit="contracts")
        contract_filters = (Contract.contract_details_ib == None,)
        contracts = self._contracts_db_manager.get_by_filters(
            filters=contract_filters)
        progress_bar.total = len(contracts)
        _logger.info(f"Found {len(contracts)} contracts without IB-details.")
        self._tws_connector.connect()
        for contract in contracts:
            if signal_handler.is_exit_requested():
                break
            self._handle_contract(contract=contract)
            progress_bar.update(inc=1)
        self._orm_session.close()
        self._tws_connector.disconnect()

    def _handle_contract(self, contract: Contract) -> None:
        try:
            details = self._tws_connector.download_contract_details(
                contract=contract)
        except (RequestError, InvalidDataReceivedError) as e:
            _logger.debug(e.message)  # todo
        else:
            self._details_db_manager.add_to_db(details=details)
            self._orm_session.commit()
