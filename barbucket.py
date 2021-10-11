import logging
import logging.handlers

from pathlib import Path

from barbucket.mediator import Mediator
from barbucket import cli as cli


if __name__ == '__main__':
    """Docstring"""

    # Setup logging
    def my_filenamer(filename):
        new_name = filename.replace(".txt.", "_") + ".txt"
        return new_name

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARN)
    console_formatter = logging.Formatter("%(message)s")
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=Path.home() / ".barbucket/logfile.txt",
        when='midnight')
    file_handler.namer = my_filenamer
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s;%(name)s;%(levelname)s;%(message)s")
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    logger = logging.getLogger(__name__)
    logger.debug("Application started.")

    # Create mediator
    mediator = Mediator(
        cli=cli
    )

    # Run Cli
    mediator.notify("run_cli")
