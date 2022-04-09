import logging
from typing import List

from bs4 import BeautifulSoup

from barbucket.domain_model.data_classes import Contract
from barbucket.domain_model.types import Api, Exchange, ContractType, ApiNotationTranslator
import barbucket.util.custom_exceptions as custom_exceptions


_logger = logging.getLogger(__name__)


class ContractExtractor():
    def __init__(self, api_notation_translator: ApiNotationTranslator) -> None:
        self._api_notation_translator = api_notation_translator

    def extract_contracts(self, html: str, exchange: Exchange) -> List[Contract]:
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all(
            'table', class_='table table-striped table-bordered')
        rows = tables[2].tbody.find_all('tr')
        website_contracts = []
        for row in rows:
            columns = row.find_all('td')
            exchange_symbol = self._api_notation_translator.get_ticker_symbol_from_api_notation(
                name=columns[2].text.strip(),
                api=Api.IB)
            broker_symbol = self._api_notation_translator.get_ticker_symbol_from_api_notation(
                name=columns[0].text.strip(),
                api=Api.IB)
            contract = Contract(
                contract_type=ContractType.STOCK.name,
                exchange_symbol=exchange_symbol.name,
                broker_symbol=broker_symbol.name,
                name=columns[1].text.strip(),
                currency=columns[3].text.strip(),
                exchange=exchange.name)
            website_contracts.append(contract)
        if website_contracts == []:
            raise custom_exceptions.InvalidDataReceivedError(
                "No contracts in webpage found.")
        _logger.debug(f"Found {len(website_contracts)} contracts in webpage.")
        return website_contracts
