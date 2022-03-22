import logging
import datetime

from sqlalchemy.orm import Session

from barbucket.datasource_connectors.ib_exchange_listing_reader import IbExchangeListingReader
from barbucket.persistence.data_managers import ContractsDbManager
from barbucket.domain_model.data_classes import Contract
from barbucket.domain_model.types import ContractType, Exchange
from barbucket.util.custom_exceptions import ExitSignalDetectedError


_logger = logging.getLogger(__name__)


class ContractSyncProcessor():
    def __init__(self,
                 listing_reader: IbExchangeListingReader,
                 contracts_db_manager: ContractsDbManager,
                 orm_session: Session) -> None:
        self._listing_reader = listing_reader
        self._contracts_db_manager = contracts_db_manager
        self._orm_session = orm_session
        self.override_user_acknowledge = False

    def sync_contracts_to_listing(self, exchange: Exchange) -> None:
        # Get contracts
        try:
            web_contracts = self._listing_reader.read_ib_exchange_listing(
                exchange=exchange)
        except ExitSignalDetectedError as e:
            _logger.info(e.message)
            return
        contract_filters = (
            Contract.contract_type == ContractType.STOCK.name,
            Contract.exchange == exchange.name)
        db_contracts = self._contracts_db_manager.get_by_filters(
            filters=contract_filters)
        wc = set(web_contracts)
        dc = set(db_contracts)
        removed_contracts = dc.difference(wc)
        added_contracts = wc.difference(dc)

        # Execute
        if not self.override_user_acknowledge:
            ua = self._user_acknowledge(n_remove=len(removed_contracts),
                                        n_add=len(added_contracts))
        if self.override_user_acknowledge or ua:
            for contract in removed_contracts:
                self._contracts_db_manager.delete_from_db(contract=contract)
            for contract in added_contracts:
                self._contracts_db_manager.add_to_db(contract=contract)
            self._orm_session.commit()
        else:
            _logger.info("Aborted.")
        self._orm_session.close()

    # ~~~~~~~~~~~~~~~~~~~~ private methods ~~~~~~~~~~~~~~~~~~~~

    def _user_acknowledge(self, n_remove: int, n_add: int) -> bool:
        print(f"{n_add} new contracts will be added and {n_remove} deprecated "
              f"contracts will be removed. Do you want to continue? (Y/N): ",
              end="")
        message = input()
        return message.upper() == "Y"
