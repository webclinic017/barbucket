from pathlib import Path

from barbucket.business_logic.universe_processor import UniverseProcessor
from barbucket.domain_model.data_classes import Base
from barbucket.persistence.connectionstring_assembler import ConnectionStringAssembler
from barbucket.persistence.data_managers import ContractsDbManager, UniverseDbManager
from barbucket.persistence.orm_connector import OrmConnector
from barbucket.util.config_reader import ConfigReader


def build_universe_processor():
    config_reader = ConfigReader(
        filepath=Path.home() / ".barbucket/config.cfg")

    connstring_assembler = ConnectionStringAssembler(
        config_reader=config_reader)
    orm_connector = OrmConnector(
        connstring_assembler=connstring_assembler,
        base_class=Base)
    orm_session = orm_connector.get_session()

    universe_db_manager = UniverseDbManager(orm_session=orm_session)

    contracts_db_manager = ContractsDbManager(orm_session=orm_session)

    universe_processor = UniverseProcessor(
        universe_db_manager=universe_db_manager,
        contracts_db_manager=contracts_db_manager,
        orm_session=orm_session)

    return universe_processor
