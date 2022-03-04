import logging
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from barbucket.domain_model.data_classes import Contract
from barbucket.domain_model.types import Api, Exchange, ContractType, ApiNotationTranslator


_logger = logging.getLogger(__name__)


class HtmlContractExtractor():

    @classmethod
    def extract_contracts(cls, html: str, contract_type: ContractType,
                          exchange: Exchange) -> List[Contract]:
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table',
                               class_='table table-striped table-bordered')
        rows = tables[2].tbody.find_all('tr')
        website_contracts = []
        for row in rows:
            columns = row.find_all('td')
            exchange_symbol = ApiNotationTranslator.get_ticker_symbol_from_api_notation(
                name=columns[2].text.strip(),
                api=Api.IB)
            broker_symbol = ApiNotationTranslator.get_ticker_symbol_from_api_notation(
                name=columns[0].text.strip(),
                api=Api.IB)
            contract = Contract(
                contract_type_from_listing=contract_type.name,
                exchange_symbol=exchange_symbol.name,
                broker_symbol=broker_symbol.name,
                name=columns[1].text.strip(),
                currency=columns[3].text.strip(),
                exchange=exchange.name)
            website_contracts.append(contract)
        # todo: log amount
        return website_contracts

    # @classmethod
    # def extract_data_multipage(cls, html: str) -> List[Contract]:
    #     soup = BeautifulSoup(html, 'html.parser')
    #     tables = soup.find_all(
    #         'table',
    #         class_='table table-striped table-bordered')
    #     rows = tables[2].tbody.find_all('tr')

    #     for row in rows:
    #         cols = row.find_all('td')
    #         row_dict = {
    #             'type': self.cont_type,
    #             'broker_symbol': Symbol.decode(
    #                 name=cols[0].text.strip(),
    #                 from_api=Api.IB),
    #             'name': cols[1].text.strip(),
    #             'exchange_symbol': Symbol.decode(
    #                 name=cols[2].text.strip(),
    #                 from_api=Api.IB),
    #             'currency': cols[3].text.strip(),
    #             'exchange': Exchange.decode(
    #                 name=self._exchange,
    #                 from_api=Api.IB)}
    #         self._website_data.append(row_dict)
    #     # todo: log ammount
    #     # todo: handle ammount == 0

    # @classmethod
    # def _validate_result(cls, contracts):
    #     if len(contracts) == 0:
    #         raise WebscrapingReturnedNoResultError


# class WebscrapingReturnedNoResultError(Exception):
#     """Obviously something went wrong."""

#     def __init__(self, message) -> None:
#         self.message = message
#         super().__init__(message)
