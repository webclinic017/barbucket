from logging import getLogger

from barbucket.datasource_connectors.html_corrector import HtmlCorrector
from barbucket.domain_model.types import Exchange


_logger = getLogger(__name__)
_logger.debug(f"--------- ---------- Testing HtmlCorrector")


def test_correct_ib_error_singlepage() -> None:
    with open("tests/_resources/datasource_connectors/dummy-listing_xetra_etf_singlepage.html", 'r') as filereader:
        lines = filereader.readlines()
    dummy_html = "".join(lines)
    corrected_html = HtmlCorrector.correct_ib_error_singlepage(html=dummy_html)
    for line in corrected_html.splitlines():
        if (('        <td align="left" valign="middle">' in line)
                and ("href" not in line)):
            assert "</a>" not in line
