import configparser
from pathlib import Path
from typing import List


class ConfigReader():
    """Read config values from existing configuration file."""

    _PARSER = configparser.ConfigParser(allow_no_value=True)
    _CONFIG_FILE_PATH = Path.home() / ".barbucket/config.ini"
    # Todo: Reads empty file when not initialized. initialization happens afterwards.

    def __init__(self) -> None:
        self._PARSER.read(self._CONFIG_FILE_PATH)

    def get_config_value_single(self, section: str, option: str) -> str:
        """Reads a single config value"""
        return self._PARSER.get(section, option)

    def get_config_value_list(self, section: str, option: str) -> List[str]:
        """Reads a config value list"""
        value = self._PARSER.get(section, option)
        value = value.split(",")  # split by comma and change to list
        return value
