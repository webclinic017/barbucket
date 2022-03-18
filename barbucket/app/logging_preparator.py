import logging
import logging.handlers
from pathlib import Path


class LoggingPreparator():

    def setup_logging(self) -> None:

        def my_file_namer(filename):
            new_name = filename.replace(".log.", "_") + ".log"
            return new_name

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
        logger.debug(
            "--------------------------------------- Application started")
