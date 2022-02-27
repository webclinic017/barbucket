import logging
import logging.handlers
from pathlib import Path
from typing import Generator

import pytest

from barbucket.connectionstring_assembler import ConnectionStringAssembler
from barbucket.orm_connector import OrmConnector


_logger: logging.Logger


@pytest.fixture(scope="session", autouse=True)
def setup_testing() -> None:
    _create_directories()
    _setup_logging()
    _logger.debug("---------- ---------- ---------- Testing started")


@pytest.fixture
def mock_connstr_assembler() -> Generator:
    _logger.debug(f"---------- Fixture: mock_connstr_assembler")
    yield MockConnectionStringAssembler()


class MockConnectionStringAssembler(ConnectionStringAssembler):
    # override
    def __init__(self) -> None:
        pass

    # override
    @classmethod
    def get_connection_string(cls) -> str:
        return "sqlite:///:memory:"


@pytest.fixture
def orm_connector(mock_connstr_assembler: MockConnectionStringAssembler) -> Generator:
    _logger.debug(f"---------- Fixture: orm_connector")
    oc = OrmConnector(connstring_assembler=mock_connstr_assembler)
    yield oc


def _create_directories() -> None:
    Path.mkdir(Path.home() / ".barbucket/logs", exist_ok=True)


def _setup_logging() -> None:
    # Get logger instance
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Add file handler
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=Path.home() / ".barbucket/logs/logfile_tests.log",
        when='midnight')
    file_handler.namer = _my_file_namer
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Set module logger
    global _logger
    _logger = root_logger


def _my_file_namer(filename: str) -> str:
    new_name = filename.replace(".log.", "_") + ".log"
    return new_name
