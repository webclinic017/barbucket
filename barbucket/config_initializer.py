from pathlib import Path
import logging
from shutil import copyfile


class ConfigInitializer():
    """Initialize the configuration file, if not present"""

    _CONFIG_FILE_PATH = Path.home() / ".barbucket/config.ini"

    def __init__(self) -> None:
        pass

    def initalize_config(self) -> None:
        """Initializes the configuration file, if not present"""
        self._create_directories()
        self._create_config_file(
            source_path="default_config.ini",
            destination_path=self._CONFIG_FILE_PATH)

    def _create_directories(self) -> None:
        """Creates barbucket directories, if not present"""
        try:
            Path.mkdir((Path.home() / ".barbucket/tv_screener"), parents=True)
        except FileExistsError:
            logging.debug(f"Created directories `~/.barbucket/tv_screener`")
        else:
            logging.debug(f"Necessary directories already exist.")

    def _create_config_file(
            self, source_path: Path,
            destination_path: Path) -> None:
        """Creates file with default config if none exists"""
        if Path.is_file(destination_path):
            logging.debug(f"Config file already exists.")
        else:
            copyfile(source_path, destination_path)
            logging.debug(f"Created config file from default file.")
