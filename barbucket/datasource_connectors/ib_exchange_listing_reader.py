import time
import logging
from typing import List
from abc import ABC, abstractmethod

import enlighten

from barbucket.domain_model.data_classes import Contract
from barbucket.util.signal_handler import SignalHandler
from barbucket.util.custom_exceptions import ExitSignalDetectedError
from barbucket.domain_model.types import Exchange
from barbucket.datasource_connectors.html_downloader import HtmlDownloader
from barbucket.datasource_connectors.html_corrector import HtmlCorrector
from barbucket.datasource_connectors.contract_extractor import ContractExtractor
from barbucket.datasource_connectors.pagecount_extractor import PageCountExtractor


_logger = logging.getLogger(__name__)


class IbExchangeListingReader(ABC):
    """Abstract baseclass for exchange listings readers"""

    def __init__(self,
                 downloader: HtmlDownloader,
                 corrector: HtmlCorrector,
                 contract_extractor: ContractExtractor) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_ib_exchange_listing(self, exchange: Exchange) -> List[Contract]:
        raise NotImplementedError


class IbExchangeListingSinglepageReader(IbExchangeListingReader):
    """Exchange listings reader for singlepage listings"""

    def __init__(self,
                 downloader: HtmlDownloader,
                 corrector: HtmlCorrector,
                 contract_extractor: ContractExtractor) -> None:
        self._downloader = downloader
        self._corrector = corrector
        self._contract_extractor = contract_extractor

    def read_ib_exchange_listing(self, exchange: Exchange) -> List[Contract]:
        """Read contracts from exchange listing website

        :param cont_type: Contracts type to read
        :param exchange: Exchange to read from
        :type exchange: Exchange
        :return: Contracts from website
        :rtype: List[Dict[str, Any]]
        """

        html = self._downloader.get_weblisting_singlepage(
            exchange=exchange)
        # html = self._corrector.correct_ib_error_singlepage(html=html)
        web_contracts = self._contract_extractor.extract_contracts(
            html, exchange=exchange)
        return web_contracts


class IbExchangeListingMultipageReader(IbExchangeListingReader):
    """Exchange listings reader for multipage listings"""

    def __init__(self,
                 downloader: HtmlDownloader,
                 corrector: HtmlCorrector,
                 pagecount_extractor: PageCountExtractor,
                 contract_extractor: ContractExtractor) -> None:
        self._downloader = downloader
        self._corrector = corrector
        self._pagecount_extractor = pagecount_extractor
        self._contract_extractor = contract_extractor

    def read_ib_exchange_listing(self, exchange: Exchange) -> List[Contract]:
        """Read contracts from exchange listing website

        :param type_: Contracts type to read
        :type type_: str
        :param exchange: Exchange to read from
        :type exchange: str
        :return: Contracts from website
        :rtype: List[Dict[str, Any]]
        """

        web_contracts: List[Contract] = []
        current_page = 1
        page_count = 1
        signal_handler = SignalHandler()
        pb_manager = enlighten.get_manager()
        progress_bar = pb_manager.counter(total=0, desc="Pages", unit="pages")

        while current_page <= page_count:
            html = self._downloader.get_weblisting_multipage(
                exchange=exchange, page=current_page)
            # html = self._corrector.correct_ib_error_multipage(html=html)
            if current_page == 1:
                page_count = self._pagecount_extractor.get_page_count(
                    html)
                progress_bar.total = page_count
            page_contracts = self._contract_extractor.extract_contracts(
                html=html, exchange=exchange)
            _logger.debug(f"Scraped IB exchange listing for '{exchange.name}', "
                          f"page {current_page}.")
            web_contracts += page_contracts
            if signal_handler.is_exit_requested():
                raise ExitSignalDetectedError(
                    "User pressed 'Ctrl+C'.")  # is handled above
            progress_bar.update(incr=1)
            current_page += 1
            if current_page != page_count:
                # show some mercy to IB webserver and dont get yourself banned
                time.sleep(3)
        return web_contracts
