import time
import logging
from typing import List
from abc import ABC, abstractmethod

import enlighten

from barbucket.domain_model.data_classes import Contract
from barbucket.util.signal_handler import SignalHandler
from barbucket.domain_model.types import Exchange
from barbucket.datasource_connectors.exchange_listing_downloader import ExchangeistingDownloader
from barbucket.datasource_connectors.html_corrector import HtmlCorrector
from barbucket.datasource_connectors.html_contract_extractor import HtmlContractExtractor
from barbucket.datasource_connectors.pagecount_extractor import PageCountExtractor


_logger = logging.getLogger(__name__)


class IbExchangeListingReader(ABC):
    """Abstract baseclass for exchange listings readers"""

    def __init__(self,
                 downloader: ExchangeistingDownloader,
                 corrector: HtmlCorrector,
                 contract_extractor: HtmlContractExtractor) -> None:
        raise NotImplementedError

    @abstractmethod
    def read_ib_exchange_listing(self, exchange: Exchange) -> List[Contract]:
        raise NotImplementedError


class IbExchangeListingSinglepageReader(IbExchangeListingReader):
    """Exchange listings reader for singlepage listings"""
    _downloader: ExchangeistingDownloader
    _corrector: HtmlCorrector
    _contract_extractor: HtmlContractExtractor

    def __init__(self,
                 downloader: ExchangeistingDownloader,
                 corrector: HtmlCorrector,
                 contract_extractor: HtmlContractExtractor) -> None:
        IbExchangeListingSinglepageReader._downloader = downloader
        IbExchangeListingSinglepageReader._corrector = corrector
        IbExchangeListingSinglepageReader._contract_extractor = contract_extractor

    @classmethod
    def read_ib_exchange_listing(cls, exchange: Exchange) -> List[Contract]:
        """Read contracts from exchange listing website

        :param cont_type: Contracts type to read
        :param exchange: Exchange to read from
        :type exchange: Exchange
        :return: Contracts from website
        :rtype: List[Dict[str, Any]]
        """

        html = cls._downloader.get_weblisting_singlepage(
            exchange=exchange)
        # html = cls._corrector.correct_ib_error_singlepage(html=html)
        web_contracts = cls._contract_extractor.extract_contracts(
            html, exchange=exchange)
        return web_contracts


class IbExchangeListingMultipageReader(IbExchangeListingReader):
    """Exchange listings reader for multipage listings"""
    _downloader: ExchangeistingDownloader
    _corrector: HtmlCorrector
    _pagecount_extractor: PageCountExtractor
    _contract_extractor: HtmlContractExtractor

    def __init__(self,
                 downloader: ExchangeistingDownloader,
                 corrector: HtmlCorrector,
                 pagecount_extractor: PageCountExtractor,
                 contract_extractor: HtmlContractExtractor) -> None:
        IbExchangeListingMultipageReader._downloader = downloader
        IbExchangeListingMultipageReader._corrector = corrector
        IbExchangeListingMultipageReader._pagecount_extractor = pagecount_extractor
        IbExchangeListingMultipageReader._contract_extractor = contract_extractor

    @classmethod
    def read_ib_exchange_listing(cls, exchange: Exchange) -> List[Contract]:
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
            html = cls._downloader.get_weblisting_multipage(
                exchange=exchange, page=current_page)
            # html = cls._corrector.correct_ib_error_multipage(html=html)
            if current_page == 1:
                progress_bar.total = cls._pagecount_extractor.get_page_count(
                    html)
            page_contracts = cls._contract_extractor.extract_contracts(
                html=html, exchange=exchange)
            _logger.debug(f"Scraped IB exchange listing for '{exchange.name}', "
                          f"page {current_page}.")
            web_contracts += page_contracts
            signal_handler.is_exit_requested()  # raises ex to exit
            progress_bar.update(incr=1)
            current_page += 1
            if current_page != page_count:
                # show some mercy to IB webserver and dont get yourself banned
                time.sleep(3)
        return web_contracts
