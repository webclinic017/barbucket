import logging
import logging.handlers
from pathlib import Path

import pytest


def create_directories():
    Path.mkdir(Path.home() / ".barbucket/logs", exist_ok=True)


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=Path.home() / ".barbucket/logs/logfile_tests.log",
        when='midnight')
    file_handler.namer = my_file_namer
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)


def my_file_namer(filename):
    new_name = filename.replace(".log.", "_") + ".log"
    return new_name


@pytest.fixture(scope="session", autouse=True)
def setup_session():
    create_directories()
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.debug("---------- ---------- ---------- Testing started")
