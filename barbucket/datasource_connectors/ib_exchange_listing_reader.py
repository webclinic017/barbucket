import time
import logging
from typing import Any, Dict, List
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
import requests
import enlighten

from barbucket.domain_model.data_classes import Contract
from barbucket.util.signal_handler import SignalHandler
from barbucket.domain_model.types import Api, Exchange, TickerSymbol, ContractType, ApiNotationTranslator
from barbucket.datasource_connectors.exchange_listing_downloader import ExchangeistingDownloader
from barbucket.datasource_connectors.html_corrector import HtmlCorrector
from barbucket.datasource_connectors.html_contract_extractor import HtmlContractExtractor


_logger = logging.getLogger(__name__)


class IbExchangeListingReader(ABC):
    """Abstract baseclass for exchange listings readers"""

    def __init__(self,
                 downloader: ExchangeistingDownloader,
                 corrector: HtmlCorrector,
                 extractro: HtmlContractExtractor) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_ib_exchange_listing(self, cont_type: ContractType,
                                 exchange: Exchange) -> List[Contract]:
        raise NotImplementedError


class IbExchangeListingSinglepageReader(IbExchangeListingReader):
    """Exchange listings reader for singlepage listings"""
    _downloader: ExchangeistingDownloader
    _corrector: HtmlCorrector
    _extractor: HtmlContractExtractor
    _cont_type: ContractType
    _exchange: Exchange

    def __init__(self,
                 downloader: ExchangeistingDownloader,
                 corrector: HtmlCorrector,
                 extractor: HtmlContractExtractor) -> None:
        IbExchangeListingSinglepageReader._downloader = downloader
        IbExchangeListingSinglepageReader._corrector = corrector
        IbExchangeListingSinglepageReader._extractor = extractor

    @classmethod
    def read_ib_exchange_listing(cls, cont_type: ContractType,
                                 exchange: Exchange) -> List[Contract]:
        """Read contracts from exchange listing website

        :param cont_type: Contracts type to read
        :type cont_type: ContractType
        :param exchange: Exchange to read from
        :type exchange: Exchange
        :return: Contracts from website
        :rtype: List[Dict[str, Any]]
        """

        cls._cont_type = cont_type
        cls._exchange = exchange
        html = cls._downloader.get_weblisting_singlepage(
            exchange=cls._exchange)
        html = cls._corrector.correct_ib_error_singlepage(html=html)
        contracts = cls._extractor.extract_contracts(
            html, contract_type=cls._cont_type, exchange=cls._exchange)
        return contracts


# class IbExchangeListingMultipageReader(IbExchangeListingReader):
#     """Exchange listings reader for multipage listings"""

#     def __init__(self) -> None:
#         self._signal_handler = SignalHandler()
#         self._current_page = 1
#         self._page_count = 1
#         self._html: str = ""
#         self._website_data: Any = []
#         self.cont_type: str = ""
#         self._exchange: str = ""
#         manager = enlighten.get_manager()
#         self._pbar = manager.counter(
#             total=0,
#             desc="Pages", unit="pages")

#     def read_ib_exchange_listing(self, type_: str,
#                                  exchange: str) -> List[Dict[str, Any]]:
#         """Read contracts from exchange listing website

#         :param type_: Contracts type to read
#         :type type_: str
#         :param exchange: Exchange to read from
#         :type exchange: str
#         :return: Contracts from website
#         :rtype: List[Dict[str, Any]]
#         """

#         self.cont_type = type_
#         self._exchange = Exchange.encode(name=exchange, to_api=Api.IB)

#         while self._current_page <= self._page_count:
#             self._get_html()
#             if self._current_page == 1:
#                 self._set_page_count()
#             self._correct_ib_error()
#             self._extract_data()
#             _logger.debug(
#                 f"Scraped IB exchange listing for {self._exchange}, page "
#                 f"{self._current_page}.")
#             self._signal_handler.is_exit_requested()  # raises ex to exit
#             self._pbar.update(incr=1)
#             self._current_page += 1
#             if self._current_page != self._page_count:
#                 time.sleep(3)  # show some mercy to IB webserver
#         return self._website_data

#     def _set_page_count(self) -> None:
#         soup = BeautifulSoup(self._html, 'html.parser')
#         pagination_tables = soup.find_all('ul', class_='pagination')
#         page_buttons = pagination_tables[0].find_all('li')
#         self._page_count = int(page_buttons[-2].text)
#         self._pbar.total = self._page_count
#         # todo: handle errors

#     def _get_html(self) -> None:
#         url = (f"https://www.interactivebrokers.com/en/index.php?f=2222"
#                f"&exch={self._exchange}&showcategories=STK&p=&cc=&limit="
#                f"100&page={self._current_page}")
#         self._html = requests.get(url).text
