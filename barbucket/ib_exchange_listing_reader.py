import time
import logging
from typing import Any, Dict, List
from abc import ABC, abstractmethod

from bs4 import BeautifulSoup
import requests
import enlighten

from .signal_handler import SignalHandler
from .encodings import Api, Exchange, Symbol

logger = logging.getLogger(__name__)


class IbExchangeListingReader(ABC):
    """Abstract baseclass for exchange listings readers"""

    @abstractmethod
    def read_ib_exchange_listing(self, ctype: str, exchange: str) -> Any:
        raise NotImplementedError


class IbExchangeListingSinglepageReader(IbExchangeListingReader):
    """Exchange listings reader for singlepage listings"""

    def __init__(self) -> None:
        self.__html: str = ""
        self.__ctype: str = ""
        self.__exchange: str = ""

    def read_ib_exchange_listing(
            self,
            ctype: str,
            exchange: str) -> List[Dict[str, Any]]:
        """Read contracts from exchange listing website

        :param ctype: Contracts type to read
        :type ctype: str
        :param exchange: Exchange to read from
        :type exchange: str
        :return: Contracts from website
        :rtype: List[Dict[str, Any]]
        """

        self.__ctype = ctype
        self.__exchange = Exchange.encode(name=exchange, to_api=Api.IB)
        self.__get_html()
        self.__correct_ib_error()
        contracts = self.__extract_data()
        self.__validate_result(contracts)
        return contracts

    def __get_html(self) -> None:
        url = (
            f"https://www.interactivebrokers.com/en/index.php?f=567&exch="
            f"{self.__exchange}")
        self.__html = requests.get(url).text

    def __correct_ib_error(self) -> None:
        """Website HTML contains structural errors that prevent parsing."""

        old_lines = self.__html.splitlines()
        new_lines = []
        corrections = 0
        for line in old_lines:
            if (('        <td align="left" valign="middle">' in line)
                    and ("href" not in line)):
                line = line.replace("</a>", "")
                corrections += 1
            new_lines.append(line)
        self.__html = "".join(new_lines)
        if corrections == 0:
            logger.debug(
                f"IB error for singlepage listings no longer present. Checked "
                f"{len(old_lines)} lines.")

    def __extract_data(self) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(self.__html, 'html.parser')
        tables = soup.find_all(
            'table',
            class_='table table-striped table-bordered')

        rows = tables[2].tbody.find_all('tr')
        website_contracts = []
        for row in rows:
            columns = row.find_all('td')
            row_dict = {
                'type': self.__ctype,
                'broker_symbol': Symbol.decode(
                    name=columns[0].text.strip(),
                    from_api=Api.IB),
                'name': columns[1].text.strip(),
                'exchange_symbol': Symbol.decode(
                    name=columns[2].text.strip(),
                    from_api=Api.IB),
                'currency': columns[3].text.strip(),
                'exchange': Exchange.decode(
                    name=self.__exchange,
                    from_api=Api.IB)}
            website_contracts.append(row_dict)
        # todo: log amount
        return website_contracts

    def __validate_result(self, contracts):
        if len(contracts) == 0:
            raise WebscrapingReturnedNoResultError


class IbExchangeListingMultipageReader(IbExchangeListingReader):
    """Exchange listings reader for multipage listings"""

    def __init__(self) -> None:
        self.__signal_handler = SignalHandler()
        self.__current_page = 1
        self.__page_count = 1
        self.__html: str = ""
        self.__website_data: Any = []
        self.__ctype: str = ""
        self.__exchange: str = ""
        manager = enlighten.get_manager()
        self.__pbar = manager.counter(
            total=0,
            desc="Pages", unit="pages")

    def read_ib_exchange_listing(
            self,
            ctype: str,
            exchange: str) -> List[Dict[str, Any]]:
        """Read contracts from exchange listing website

        :param ctype: Contracts type to read
        :type ctype: str
        :param exchange: Exchange to read from
        :type exchange: str
        :return: Contracts from website
        :rtype: List[Dict[str, Any]]
        """

        self.__ctype = ctype
        self.__exchange = Exchange.encode(name=exchange, to_api=Api.IB)

        while self.__current_page <= self.__page_count:
            self.__get_html()
            if self.__current_page == 1:
                self.__set_page_count()
            self.__correct_ib_error()
            self.__extract_data()
            logger.debug(
                f"Scraped IB exchange listing for {self.__exchange}, page "
                f"{self.__current_page}.")
            self.__signal_handler.is_exit_requested()  # raises ex to exit
            self.__pbar.update(incr=1)
            self.__current_page += 1
            if self.__current_page != self.__page_count:
                time.sleep(3)  # show some mercy to IB webserver
        return self.__website_data

    def __set_page_count(self) -> None:
        soup = BeautifulSoup(self.__html, 'html.parser')
        pagination_tables = soup.find_all('ul', class_='pagination')
        page_buttons = pagination_tables[0].find_all('li')
        self.__page_count = int(page_buttons[-2].text)
        self.__pbar.total = self.__page_count
        # todo: handle errors

    def __get_html(self) -> None:
        url = (f"https://www.interactivebrokers.com/en/index.php?f=2222"
               f"&exch={self.__exchange}&showcategories=STK&p=&cc=&limit="
               f"100&page={self.__current_page}")
        self.__html = requests.get(url).text

    def __correct_ib_error(self) -> None:
        """Website HTML contains structural errors that prevent parsing."""

        if ("(click link for more details)</span></th>\n                       </th>"
                in self.__html):
            self.__html = self.__html.replace(
                "(click link for more details)</span></th>\n                       </th>\n",
                "(click link for more details)</span></th>\n")
        else:
            logger.debug(
                f"IB error for paginated listings no longer present. Checked "
                f"{len(self.__html.splitlines())} lines.")

    def __extract_data(self) -> None:
        soup = BeautifulSoup(self.__html, 'html.parser')
        tables = soup.find_all(
            'table',
            class_='table table-striped table-bordered')
        rows = tables[2].tbody.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            row_dict = {
                'type': self.__ctype,
                'broker_symbol': Symbol.decode(
                    name=cols[0].text.strip(),
                    from_api=Api.IB),
                'name': cols[1].text.strip(),
                'exchange_symbol': Symbol.decode(
                    name=cols[2].text.strip(),
                    from_api=Api.IB),
                'currency': cols[3].text.strip(),
                'exchange': Exchange.decode(
                    name=self.__exchange,
                    from_api=Api.IB)}
            self.__website_data.append(row_dict)
        # todo: log ammount
        # todo: handle ammount == 0


class WebscrapingReturnedNoResultError(Exception):
    """Obviously something went wrong."""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)
