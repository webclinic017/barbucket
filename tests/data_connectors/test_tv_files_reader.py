from typing import Generator
from pathlib import Path
from logging import getLogger

import pytest

from barbucket.datasource_connectors.tv_files_reader import TvFilesReader
from barbucket.domain_model.types import ApiNotationTranslator


_logger = getLogger(__name__)
_logger.debug(f"--------- ---------- Testing TvFilesReader")


@pytest.fixture()
def mock_tv_files_reader() -> Generator:
    _logger.debug(f"---------- Fixture: mock_tv_files_reader")
    filespath = Path("tests/_resources/datasource_connectors/")
    reader = TvFilesReader(
        files_path=filespath, api_notation_translator=ApiNotationTranslator())
    yield reader


def test_get_all_rows_count(mock_tv_files_reader: TvFilesReader) -> None:
    _logger.debug(f"---------- Test: test_get_all_rows_count")
    rows = mock_tv_files_reader.get_all_rows()
    assert len(rows) == 4


def test_get_all_rows_values(mock_tv_files_reader: TvFilesReader) -> None:
    _logger.debug(f"---------- Test: test_get_all_rows_values")
    rows = mock_tv_files_reader.get_all_rows()
    assert rows[3].ticker_symbol == "TL0"
    assert rows[3].exchange == "FWB"
    assert rows[3].country == "United States"
    assert rows[3].market_cap == 735636132073
    assert rows[3].avg_vol_30_in_curr == 818046
    assert rows[3].employees == 70757
    assert rows[3].profit == 5418659220
    assert rows[3].revenue == 25774183584


def test_get_all_rows_none(mock_tv_files_reader: TvFilesReader) -> None:
    _logger.debug(f"---------- Test: test_get_all_rows_none")
    rows = mock_tv_files_reader.get_all_rows()
    assert rows[0].market_cap == None
    assert rows[0].avg_vol_30_in_curr == None
    assert rows[0].employees == None
    assert rows[0].profit == None
    assert rows[0].revenue == None
