from configparser import ConfigParser
from pathlib import Path
from typing import List
from logging import getLogger
from shutil import copyfile
from importlib import resources


_logger = getLogger(__name__)


class ConfigReader():
    """Reads config values from a configuration file."""

    _parser: ConfigParser
    _CONFIG_FILE_PATH: Path

    def __init__(self, filepath: Path) -> None:
        ConfigReader._parser = ConfigParser(allow_no_value=True)
        ConfigReader._CONFIG_FILE_PATH = filepath
        ConfigReader._initalize()

    @classmethod
    def _initalize(cls) -> None:
        """Checks for the presence of a configuration file for the current 
        user. If not present, creates a default configuration file

        :param destination_path: Path to the configuration file
        :type destination_path: Path
        """

        destination_path = cls._CONFIG_FILE_PATH
        if Path.is_file(destination_path):
            _logger.debug(f"Config file already exists.")
        else:
            with resources.path("barbucket", "default_config.cfg") as source_path:
                copyfile(source_path, destination_path)
                _logger.info(
                    f"Created config file {destination_path} from default file.")
        cls._parser.read(cls._CONFIG_FILE_PATH)
        _logger.debug(f"Read config file.")

    @classmethod
    def get_config_value_single(cls, section: str, option: str) -> str:
        """Reads a single config value from the config file

        :param section: Section of the config file
        :type section: str
        :param option: Option of the config file
        :type option: str
        :return: Value from the config file
        :rtype: str
        """

        config_value = cls._parser.get(section, option)
        _logger.debug(
            f"Read single config value from '{section}'/'{option}' as '{config_value}'.")
        return config_value

    @classmethod
    def get_config_value_list(cls, section: str, option: str) -> List[str]:
        """Reads a config value list from the config file

        :param section: Section of the config file
        :type section: str
        :param option: Option of the config file
        :type option: str
        :return: Values from the config file
        :rtype: List[str]
        """

        config_value = cls._parser.get(section, option)
        # split by comma and change to list
        list_config_value = config_value.split(",")
        _logger.debug(
            f"Read list config value from '{section}'/'{option}' as '{list_config_value}'.")
        return list_config_value
