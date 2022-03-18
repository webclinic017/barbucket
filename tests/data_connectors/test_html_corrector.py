from logging import getLogger

from barbucket.datasource_connectors.html_corrector import HtmlCorrector
from barbucket.domain_model.types import Exchange


_logger = getLogger(__name__)
_logger.debug(f"--------- ---------- Testing HtmlCorrector")


def test_correct_ib_error_singlepage() -> None:
    _logger.debug(f"---------- Test: test_correct_ib_error_singlepage")
    dummy_file = "tests/_resources/datasource_connectors/dummy-listing_xetra_etfs_singlepage.html"
    with open(dummy_file, 'r') as filereader:
        lines = filereader.readlines()
    dummy_html = "".join(lines)
    hc = HtmlCorrector()
    corrected_html = hc.correct_ib_error_singlepage(html=dummy_html)
    for line in corrected_html.splitlines():
        if (('        <td align="left" valign="middle">' in line)
                and ("href" not in line)):
            assert "</a>" not in line


# def test_correct_ib_error_multipage() -> None:
#     _logger.debug(f"---------- Test: test_correct_ib_error_multipage")
#     with open("tests/_resources/datasource_connectors/dummy-listing_xetra_etfs_singlepage.html", 'r') as filereader:
#         lines = filereader.readlines()
#     dummy_html = "".join(lines)
#     corrected_html = HtmlCorrector.correct_ib_error_singlepage(html=dummy_html)
#     for line in corrected_html.splitlines():
#         if (('        <td align="left" valign="middle">' in line)
#                 and ("href" not in line)):
#             assert "</a>" not in line
