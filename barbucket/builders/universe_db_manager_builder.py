from pathlib import Path

from barbucket.domain_model.data_classes import Base
from barbucket.persistence.connectionstring_assembler import ConnectionStringAssembler
from barbucket.persistence.data_managers import UniverseDbManager
from barbucket.persistence.orm_connector import OrmConnector
from barbucket.util.config_reader import ConfigReader


def build_universe_db_manager():
    config_reader = ConfigReader(
        filepath=Path.home() / ".barbucket/config/config.cfg")

    connstring_assembler = ConnectionStringAssembler(
        config_reader=config_reader)
    orm_connector = OrmConnector(
        connstring_assembler=connstring_assembler,
        base_class=Base)
    orm_session = orm_connector.get_session()

    universe_db_manager = UniverseDbManager(orm_session=orm_session)

    return universe_db_manager
