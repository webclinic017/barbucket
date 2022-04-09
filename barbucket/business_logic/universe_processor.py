import logging
from typing import List

from sqlalchemy.orm import Session

from barbucket.persistence.data_managers import UniverseDbManager, ContractsDbManager
from barbucket.domain_model.data_classes import Contract


_logger = logging.getLogger(__name__)


class UniverseProcessor():

    def __init__(self,
                 universe_db_manager: UniverseDbManager,
                 contracts_db_manager: ContractsDbManager,
                 orm_session: Session) -> None:
        self._universe_db_manager = universe_db_manager
        self._contracts_db_manager = contracts_db_manager
        self._orm_session = orm_session

    def create_universe(self, name: str, contract_ids: str) -> None:
        """Create new universe"""

        name = name.upper()
        if self._universe_db_manager.is_existing(name=name):
            _logger.info(f"Universe '{name}' already exists.")
            return
        contract_id_list = [int(n) for n in contract_ids.split(",")]
        filters = (Contract.id.in_(contract_id_list),)
        contracts = self._contracts_db_manager.get_by_filters(filters=filters)
        self._universe_db_manager.create_universe(
            name=name, contracts=contracts)
        self._orm_session.commit()
        _logger.info(f"Created universe '{name}' with {len(contract_id_list)} "
                     f"contracts.")

    def is_existing(self, name: str) -> bool:
        return self._universe_db_manager.is_existing(name=name)

    def get_universes(self) -> List[str]:
        universes = self._universe_db_manager.get_universes()
        _logger.info(f"Existing universes: {universes}")
        return universes

    def delete_universe(self, name: str) -> None:
        name = name.upper()
        if not self._universe_db_manager.is_existing(name=name):
            _logger.info(f"Universe '{name}' does not exist.")
            return
        print(f"Are you sure you want to delete universe '{name}'? (y/n): ",
              end="")
        if input().upper() == "Y":
            self._universe_db_manager.delete_universe(name=name)
            self._orm_session.commit()
            _logger.info(f"Deleted universe '{name}'.")
        else:
            _logger.info("Aborted.")
