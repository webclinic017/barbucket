from logging import getLogger

import requests

from barbucket.datasource_connectors.html_downloader import HtmlDownloader
from barbucket.domain_model.types import Exchange, ApiNotationTranslator

_logger = getLogger(__name__)
_logger.debug(f"--------- ---------- Testing ExchangeListingDownloader")


def mock_get(url: str):
    class MockResponse():
        text = url

    return MockResponse()


def test_get_weblisting_singlepage(monkeypatch) -> None:
    """ """
    _logger.debug(f"---------- Test: test_get_weblisting_singlepage")
    monkeypatch.setattr(requests, "get", mock_get)
    downloader = HtmlDownloader(
        api_notation_translator=ApiNotationTranslator())
    expected_html = "https://www.interactivebrokers.com/en/index.php?f=567&exch=IBIS"
    actual_html = downloader.get_weblisting_singlepage(exchange=Exchange.XETRA)
    assert actual_html == expected_html


def test_get_weblisting_multipage(monkeypatch) -> None:
    """ """
    _logger.debug(f"---------- Test: test_get_weblisting_multipage")
    monkeypatch.setattr(requests, "get", mock_get)
    downloader = HtmlDownloader(
        api_notation_translator=ApiNotationTranslator())
    expected_html = ("https://www.interactivebrokers.com/en/index.php?f=2222"
                     "&exch=IBIS&showcategories=STK&p=&cc=&limit=100&page=5")
    actual_html = downloader.get_weblisting_multipage(
        exchange=Exchange.XETRA, page=5)
    assert actual_html == expected_html
