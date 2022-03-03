import configparser
from pathlib import Path
from typing import List
import logging
from shutil import copyfile
from importlib import resources


logger = logging.getLogger(__name__)


class ConfigReader():
    """Read config values from existing configuration file."""

    __parser = configparser.ConfigParser(allow_no_value=True)
    __CONFIG_FILE_PATH = Path.home() / ".barbucket/config.ini"
    __is_initialized = False

    def __init__(self) -> None:
        if not ConfigReader.__is_initialized:
            ConfigReader.__initalize_config(
                destination_path=ConfigReader.__CONFIG_FILE_PATH)
            ConfigReader.__is_initialized = True
        ConfigReader.__parser.read(self.__CONFIG_FILE_PATH)

    @classmethod
    def __initalize_config(cls, destination_path: Path) -> None:
        """Checks for the presence of a configuration file for the current 
        user. If not present, creates a default configuration file

        :param destination_path: Path to the configuration file
        :type destination_path: Path
        """

        with resources.path('barbucket', 'default_config.ini') as pathreader:
            source_path = pathreader
        if Path.is_file(destination_path):
            logger.debug(f"Config file already exists.")
        else:
            copyfile(source_path, destination_path)
            logger.info(
                f"Created config file {destination_path} from default file.")

    def get_config_value_single(self, section: str, option: str) -> str:
        """Reads a single config value from the config file

        :param section: Section of the config file
        :type section: str
        :param option: Option of the config file
        :type option: str
        :return: Value from the config file
        :rtype: str
        """
        return ConfigReader.__parser.get(section, option)

    def get_config_value_list(self, section: str, option: str) -> List[str]:
        """Reads a config value list from the config file

        :param section: Section of the config file
        :type section: str
        :param option: Option of the config file
        :type option: str
        :return: Values from the config file
        :rtype: List[str]
        """
        value = ConfigReader.__parser.get(section, option)
        return value.split(",")  # split by comma and change to list
