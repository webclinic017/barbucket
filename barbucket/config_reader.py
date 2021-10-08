import configparser
from pathlib import Path
from typing import List

from .config_initializer import ConfigInitializer


class ConfigReader():
    """Read config values from existing configuration file."""

    __parser = configparser.ConfigParser(allow_no_value=True)
    __CONFIG_FILE_PATH = Path.home() / ".barbucket/config.ini"
    __is_initialized = False

    def __init__(self) -> None:
        if not ConfigReader.__is_initialized:
            self.__initializer = ConfigInitializer()
            self.__initializer.initalize_config(
                ConfigReader.__CONFIG_FILE_PATH)
            ConfigReader.__is_initialized = True
        self.__parser.read(self.__CONFIG_FILE_PATH)

    def get_config_value_single(self, section: str, option: str) -> str:
        """Reads a single config value"""
        return self.__parser.get(section, option)

    def get_config_value_list(self, section: str, option: str) -> List[str]:
        """Reads a config value list"""
        value = self.__parser.get(section, option)
        value = value.split(",")  # split by comma and change to list
        return value
