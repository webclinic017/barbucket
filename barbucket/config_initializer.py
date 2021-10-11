from pathlib import Path
import logging
from shutil import copyfile

logger = logging.getLogger(__name__)


class ConfigInitializer():
    """Initialize the configuration file, if not present"""

    def __init__(self) -> None:
        pass

    def initalize_config(self, filepath: Path) -> None:
        """Initializes the configuration file, if not present"""
        self._create_directories()
        self._create_config_file(
            source_path="default_config.ini",
            destination_path=filepath)

    def _create_directories(self) -> None:
        """Creates barbucket directories, if not present"""
        try:
            Path.mkdir((Path.home() / ".barbucket/tv_screener"), parents=True)
        except FileExistsError:
            logger.debug(f"Necessary directories already exist.")
        else:
            logger.info(f"Created directories `~/.barbucket/tv_screener`")

    def _create_config_file(
            self, source_path: Path,
            destination_path: Path) -> None:
        """Creates file with default config if none exists"""
        if Path.is_file(destination_path):
            logger.debug(f"Config file already exists.")
        else:
            copyfile(source_path, destination_path)
            logger.info(
                f"Created config file {destination_path} from default file.")
