import logging
from pathlib import Path

from .cli import cli


def my_filenamer(filename):
    new_name = filename.replace(".log.", "_") + ".log"
    return new_name


def main():
    """Docstring"""

    # Setup logging
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=Path.home() / ".barbucket/logfile.log",
        when='midnight')
    file_handler.namer = my_filenamer
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    logger = logging.getLogger(__name__)
    logger.debug("---------------------------------------")
    logger.debug("Application started")

    # Run Cli
    cli()
