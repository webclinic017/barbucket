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
    _create_directory()
    _setup_logging()
    _logger.debug("---------- ---------- ---------- Testing started")


def _create_directory() -> None:
    Path.mkdir(Path.home() / ".barbucket/logs", parents=True, exist_ok=True)


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
