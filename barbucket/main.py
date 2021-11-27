import logging
from pathlib import Path

from .cli import cli


def create_directories():
    Path.mkdir(Path.home() / ".barbucket/", exist_ok=True)
    Path.mkdir(Path.home() / ".barbucket/tv_screener", exist_ok=True)
    Path.mkdir(Path.home() / ".barbucket/logs", exist_ok=True)


def my_file_namer(filename):
    new_name = filename.replace(".log.", "_") + ".log"
    return new_name


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=Path.home() / ".barbucket/logs/logfile.log",
        when='midnight')
    file_handler.namer = my_file_namer
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    logger = logging.getLogger(__name__)
    logger.debug("---------------------------------------")
    logger.debug("Application started")


def main():
    """Docstring"""

    create_directories()
    setup_logging()
    cli()  # Run cli
