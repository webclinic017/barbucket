from logging import getLogger

from barbucket.datasource_connectors.pagecount_extractor import PageCountExtractor


_logger = getLogger(__name__)
_logger.debug(f"--------- ---------- Testing PageCountExtractor")


def test_get_page_count() -> None:
    _logger.debug(f"---------- Test: test_get_page_count")
    dummy_file = "tests/_resources/datasource_connectors/dummy-listing_xetra_stocks_page5.html"
    with open(dummy_file, 'r') as filereader:
        lines = filereader.readlines()
    dummy_html = "".join(lines)
    pce = PageCountExtractor()
    actual_page_count = pce.get_page_count(html=dummy_html)
    assert actual_page_count == 22
