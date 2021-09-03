import configparser
from pathlib import Path
from typing import List


class ConfigInitializer():
    """Docstring"""

    _CONFIG_FILE_PATH = Path.home() / ".barbucket/config.ini"

    def __init__(self) -> None:
        pass

    def initalize_config(self) -> None:
        """Prepare config file, if not present"""
        self._create_directories()
        self._create_config_file(
            source_path="default_config.ini",
            destination_path=self._CONFIG_FILE_PATH)

    def _create_directories(self) -> None:
        """Create both directories if not present, throws no exception if 
        directories already present"""
        Path.mkdir(
            (Path.home() / ".barbucket/tv_screener"),
            parents=True,
            exist_ok=True)

    def _create_config_file(
            self, source_path: Path,
            destination_path: Path) -> None:
        """Create file with default config if none exists"""
        if not Path.is_file(destination_path):
            with open(source_path, 'r') as reader:
                default_config = reader.readlines()
            with open(destination_path, 'w') as writer:
                writer.writelines(default_config)


class ConfigReader():
    """Docstring"""

    _PARSER = configparser.ConfigParser(allow_no_value=True)
    _CONFIG_FILE_PATH = Path.home() / ".barbucket/config.ini"

    def __init__(self) -> None:
        """Read config file content"""
        self._PARSER.read(self._CONFIG_FILE_PATH)

    def get_config_value_single(self, section: str, option: str) -> str:
        """Read a single config value"""
        return self._PARSER.get(section, option)

    def get_config_value_list(self, section: str, option: str) -> List[str]:
        """Read a config value list"""
        value = self._PARSER.get(section, option)
        value = value.split(",")  # split by comma and change to list
        return value
