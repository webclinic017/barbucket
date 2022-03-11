from pathlib import Path

from barbucket.business_logic.contract_details_tv_processor import ContractDetailsTvProcessor
from barbucket.datasource_connectors.tv_files_reader import TvFilesReader
from barbucket.domain_model.data_classes import Base
from barbucket.domain_model.types import ApiNotationTranslator
from barbucket.persistence.connectionstring_assembler import ConnectionStringAssembler
from barbucket.persistence.data_managers import ContractsDbManager
from barbucket.persistence.data_managers import ContractDetailsTvDbManager
from barbucket.persistence.orm_connector import OrmConnector
from barbucket.util.config_reader import ConfigReader


def build_contract_details_tv_processor():
    config_reader = ConfigReader(
        filepath=Path.home() / ".barbucket/config/config.cfg")

    api_notation_translator = ApiNotationTranslator()

    connstring_assembler = ConnectionStringAssembler(
        config_reader=config_reader)
    orm_connector = OrmConnector(
        connstring_assembler=connstring_assembler,
        base_class=Base)
    session = orm_connector.get_session()

    files_reader = TvFilesReader(
        files_path=Path.home() / ".barbucket/tv_screener/",
        api_notation_translator=api_notation_translator)

    contract_details_tv_db_manager = ContractDetailsTvDbManager(
        session=session)

    contracts_db_manager = ContractsDbManager(db_session=session)

    contract_details_tv_processor = ContractDetailsTvProcessor(
        files_reader=files_reader,
        details_db_manager=contract_details_tv_db_manager,
        contracts_db_manager=contracts_db_manager,
        session=session)

    return contract_details_tv_processor
