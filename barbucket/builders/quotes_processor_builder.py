from pathlib import Path

from barbucket.api.tws_connector import TwsConnector
from barbucket.business_logic.quotes_processor import QuotesProcessor
from barbucket.domain_model.data_classes import Base
from barbucket.domain_model.types import ApiNotationTranslator
from barbucket.persistence.connectionstring_assembler import ConnectionStringAssembler
from barbucket.persistence.data_managers import QuotesDbManager, UniverseMembershipsDbManager
from barbucket.persistence.orm_connector import OrmConnector
from barbucket.util.config_reader import ConfigReader
from barbucket.util.signal_handler import SignalHandler


def build_quotes_processor():
    config_reader = ConfigReader(
        filepath=Path.home() / ".barbucket/config/config.cfg")

    signal_handler = SignalHandler()

    api_notation_translator = ApiNotationTranslator()

    connstring_assembler = ConnectionStringAssembler(
        config_reader=config_reader)

    orm_connector = OrmConnector(
        connstring_assembler=connstring_assembler,
        base_class=Base)
    session = orm_connector.get_session()

    universe_db_manager = UniverseMembershipsDbManager(db_session=session)

    quotes_db_manager = QuotesDbManager(db_session=session)

    tws_connector = TwsConnector(
        config_reader=config_reader,
        api_notation_translator=api_notation_translator)

    quotes_processor = QuotesProcessor(
        universe_db_manager=universe_db_manager,
        quotes_db_manager=quotes_db_manager,
        tws_connector=tws_connector,
        signal_handler=signal_handler,
        config_reader=config_reader)

    return quotes_processor
