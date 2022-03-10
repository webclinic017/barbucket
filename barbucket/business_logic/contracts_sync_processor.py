import logging

from sqlalchemy.orm import Session

from barbucket.datasource_connectors.ib_exchange_listing_reader import IbExchangeListingReader
from barbucket.persistence.data_managers import ContractsDbManager
from barbucket.domain_model.data_classes import Contract
from barbucket.domain_model.types import ContractType, Exchange
from barbucket.util.custom_exceptions import ExitSignalDetectedError


_logger = logging.getLogger(__name__)


class ContractSyncProcessor():
    _listing_reader: IbExchangeListingReader
    _contracts_db_manager: ContractsDbManager
    _session: Session

    def __init__(self,
                 listing_reader: IbExchangeListingReader,
                 contracts_db_manager: ContractsDbManager,
                 session: Session) -> None:
        ContractSyncProcessor._listing_reader = listing_reader
        ContractSyncProcessor._contracts_db_manager = contracts_db_manager
        ContractSyncProcessor._session = session

    @classmethod
    def sync_contracts_to_listing(cls, exchange: Exchange) -> None:

        # Get contracts
        try:
            web_contracts = cls._listing_reader.read_ib_exchange_listing(
                exchange=exchange)
        except ExitSignalDetectedError as e:
            _logger.info(e.message)
            return
        contract_filters = (
            Contract.contract_type == ContractType.STOCK.name,
            Contract.exchange == exchange.name)
        db_contracts = cls._contracts_db_manager.get_by_filters(
            filters=contract_filters)

        # Find removed contracts
        removed_contracts = []
        for contract in db_contracts:
            if contract not in web_contracts:
                cls._session.delete(contract)
                removed_contracts.append(contract)

        # Find addded contracts
        added_contracts = []
        for contract in web_contracts:
            if contract not in db_contracts:
                cls._session.add(contract)
                added_contracts.append(contract)

        # Execute
        if True:  # User acknowledge
            cls._session.commit()
        else:
            cls._session.rollback()
        cls._session.close()
