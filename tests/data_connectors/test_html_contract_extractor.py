from logging import getLogger

import requests

from barbucket.datasource_connectors.contract_extractor import ContractExtractor
from barbucket.domain_model.types import Exchange, ContractType, ApiNotationTranslator
from barbucket.domain_model.data_classes import Contract

_logger = getLogger(__name__)
_logger.debug(f"--------- ---------- Testing HtmlContractExtractor")


def test_extract_contracts() -> None:
    dummy_file = "tests/_resources/datasource_connectors/dummy-listing_xetra_etfs_singlepage.html"
    with open(dummy_file, 'r') as filereader:
        lines = filereader.readlines()
    dummy_html = "".join(lines)
    ce = ContractExtractor(
        api_notation_translator=ApiNotationTranslator())
    actual_contracts = ce.extract_contracts(
        html=dummy_html, exchange=Exchange.XETRA)

    assert len(actual_contracts) == 1098

    assert actual_contracts[0].contract_type == ContractType.STOCK.name
    assert actual_contracts[0].exchange_symbol == "X0B7"
    assert actual_contracts[0].broker_symbol == "X0B7"
    assert actual_contracts[0].name == "Coba ETC -3x WTI Oil Daily Short"
    assert actual_contracts[0].currency == "EUR"
    assert actual_contracts[0].exchange == Exchange.XETRA.name

    assert actual_contracts[-1].contract_type == ContractType.STOCK.name
    assert actual_contracts[-1].exchange_symbol == "EXSG"
    assert actual_contracts[-1].broker_symbol == "EXSG"
    assert actual_contracts[-1].name == "iShares EURO STOXX Select Dividend 30 UCITS ETF DE"
    assert actual_contracts[-1].currency == "EUR"
    assert actual_contracts[-1].exchange == Exchange.XETRA.name
