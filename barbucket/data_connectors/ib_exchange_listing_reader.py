import time
from logging import getLogger
from typing import Any, Dict, List
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
import requests
import enlighten

from barbucket.domain_model.data_classes import Contract
from barbucket.util.signal_handler import SignalHandler
from barbucket.domain_model.types import Api, Exchange, Symbol, ContractType, ApiNotationTranslator


_logger = getLogger(__name__)


class IbExchangeListingReader(ABC):
    """Abstract baseclass for exchange listings readers"""

    @abstractmethod
    def read_ib_exchange_listing(self, cont_type: ContractType,
                                 exchange: Exchange) -> List[Contract]:
        raise NotImplementedError


class IbExchangeListingSinglepageReader(IbExchangeListingReader):
    """Exchange listings reader for singlepage listings"""
    IbExchangeListingSinglepageReader._cont_type: ContractType
    IbExchangeListingSinglepageReader._exchange: Exchange

    def __init__(self) -> None:
        IbExchangeListingSinglepageReader.cont_type: ContractType
        IbExchangeListingSinglepageReader._exchange: Exchange

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

        self.cont_type = cont_type
        self._exchange = exchange
        html = self._get_html()
        html = self._correct_ib_error(html)
        contracts = self._extract_data(html)
        self._validate_result(contracts)
        return contracts

    def _get_html(self) -> str:
        ex = .encode()
        url = (
            f"https://www.interactivebrokers.com/en/index.php?f=567&exch="
            f"{self._exchange}")
        return requests.get(url).text

    def _correct_ib_error(self, html: str) -> str:
        """Website HTML contains structural errors that prevent parsing."""

        old_lines = html.splitlines()
        new_lines = []
        corrections = 0
        for line in old_lines:
            if (('        <td align="left" valign="middle">' in line)
                    and ("href" not in line)):
                line = line.replace("</a>", "")
                corrections += 1
            new_lines.append(line)
        html = "".join(new_lines)
        if corrections == 0:
            _logger.debug(
                f"IB error for singlepage listings no longer present. Checked "
                f"{len(old_lines)} lines.")
        return html

    def _extract_data(self, html: str) -> List[Contract]:
        soup = BeautifulSoup(html, 'html.parser')
        tables = soup.find_all('table',
                               class_='table table-striped table-bordered')
        rows = tables[2].tbody.find_all('tr')
        website_contracts = []
        for row in rows:
            columns = row.find_all('td')
            contract = Contract(
                contract_type_from_listing=self.cont_type,
                exchange_symbol=Symbol.decode(
                    name=columns[2].text.strip(),
                    from_api=Api.IB),
                broker_symbol=Symbol.decode(
                    name=columns[0].text.strip(),
                    from_api=Api.IB),
                name=columns[1].text.strip(),
                currency=columns[3].text.strip(),
                exchange=self._exchange)
            website_contracts.append(contract)
        # todo: log amount
        return website_contracts

    def _validate_result(self, contracts):
        if len(contracts) == 0:
            raise WebscrapingReturnedNoResultError


class IbExchangeListingMultipageReader(IbExchangeListingReader):
    """Exchange listings reader for multipage listings"""

    def __init__(self) -> None:
        self._signal_handler = SignalHandler()
        self._current_page = 1
        self._page_count = 1
        self._html: str = ""
        self._website_data: Any = []
        self.cont_type: str = ""
        self._exchange: str = ""
        manager = enlighten.get_manager()
        self._pbar = manager.counter(
            total=0,
            desc="Pages", unit="pages")

    def read_ib_exchange_listing(self, type_: str,
                                 exchange: str) -> List[Dict[str, Any]]:
        """Read contracts from exchange listing website

        :param type_: Contracts type to read
        :type type_: str
        :param exchange: Exchange to read from
        :type exchange: str
        :return: Contracts from website
        :rtype: List[Dict[str, Any]]
        """

        self.cont_type = type_
        self._exchange = Exchange.encode(name=exchange, to_api=Api.IB)

        while self._current_page <= self._page_count:
            self._get_html()
            if self._current_page == 1:
                self._set_page_count()
            self._correct_ib_error()
            self._extract_data()
            _logger.debug(
                f"Scraped IB exchange listing for {self._exchange}, page "
                f"{self._current_page}.")
            self._signal_handler.is_exit_requested()  # raises ex to exit
            self._pbar.update(incr=1)
            self._current_page += 1
            if self._current_page != self._page_count:
                time.sleep(3)  # show some mercy to IB webserver
        return self._website_data

    def _set_page_count(self) -> None:
        soup = BeautifulSoup(self._html, 'html.parser')
        pagination_tables = soup.find_all('ul', class_='pagination')
        page_buttons = pagination_tables[0].find_all('li')
        self._page_count = int(page_buttons[-2].text)
        self._pbar.total = self._page_count
        # todo: handle errors

    def _get_html(self) -> None:
        url = (f"https://www.interactivebrokers.com/en/index.php?f=2222"
               f"&exch={self._exchange}&showcategories=STK&p=&cc=&limit="
               f"100&page={self._current_page}")
        self._html = requests.get(url).text

    def _correct_ib_error(self) -> None:
        """Website HTML contains structural errors that prevent parsing."""

        if ("(click link for more details)</span></th>\n                       </th>"
                in self._html):
            self._html = self._html.replace(
                "(click link for more details)</span></th>\n                       </th>\n",
                "(click link for more details)</span></th>\n")
        else:
            _logger.debug(
                f"IB error for paginated listings no longer present. Checked "
                f"{len(self._html.splitlines())} lines.")

    def _extract_data(self) -> None:
        soup = BeautifulSoup(self._html, 'html.parser')
        tables = soup.find_all(
            'table',
            class_='table table-striped table-bordered')
        rows = tables[2].tbody.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            row_dict = {
                'type': self.cont_type,
                'broker_symbol': Symbol.decode(
                    name=cols[0].text.strip(),
                    from_api=Api.IB),
                'name': cols[1].text.strip(),
                'exchange_symbol': Symbol.decode(
                    name=cols[2].text.strip(),
                    from_api=Api.IB),
                'currency': cols[3].text.strip(),
                'exchange': Exchange.decode(
                    name=self._exchange,
                    from_api=Api.IB)}
            self._website_data.append(row_dict)
        # todo: log ammount
        # todo: handle ammount == 0


class WebscrapingReturnedNoResultError(Exception):
    """Obviously something went wrong."""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)
