from pathlib import Path

from barbucket.business_logic.contracts_sync_processor import ContractSyncProcessor
from barbucket.datasource_connectors.contract_extractor import ContractExtractor
from barbucket.datasource_connectors.html_corrector import HtmlCorrector
from barbucket.datasource_connectors.html_downloader import HtmlDownloader
from barbucket.datasource_connectors.ib_exchange_listing_reader import IbExchangeListingMultipageReader
from barbucket.datasource_connectors.pagecount_extractor import PageCountExtractor
from barbucket.domain_model.data_classes import Base
from barbucket.domain_model.types import ApiNotationTranslator
from barbucket.persistence.connectionstring_assembler import ConnectionStringAssembler
from barbucket.persistence.data_managers import ContractsDbManager
from barbucket.persistence.orm_connector import OrmConnector
from barbucket.util.config_reader import ConfigReader


def build_contracts_sync_processor():
    config_reader = ConfigReader(
        filepath=Path.home() / ".barbucket/config/config.cfg")

    api_notation_translator = ApiNotationTranslator()

    connstring_assembler = ConnectionStringAssembler(
        config_reader=config_reader)

    orm_connector = OrmConnector(
        connstring_assembler=connstring_assembler,
        base_class=Base)
    session = orm_connector.get_session()

    downloader = HtmlDownloader(
        api_notation_translator=api_notation_translator)
    corrector = HtmlCorrector()
    pagecount_extractor = PageCountExtractor()

    contract_extractor = ContractExtractor(
        api_notation_translator=api_notation_translator)

    listing_reader = IbExchangeListingMultipageReader(
        downloader=downloader,
        corrector=corrector,
        pagecount_extractor=pagecount_extractor,
        contract_extractor=contract_extractor,)

    contracts_db_manager = ContractsDbManager(db_session=session)

    contracts_sync_processor = ContractSyncProcessor(
        listing_reader=listing_reader,
        contracts_db_manager=contracts_db_manager,
        session=session)

    return contracts_sync_processor
