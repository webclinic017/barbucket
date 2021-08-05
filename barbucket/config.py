import configparser
from pathlib import Path
from typing import List


class Config():

    _parser = configparser.ConfigParser(allow_no_value=True)
    _config_file_path = None


    def __init__(self,) -> None:
        """Prepare config file and read content"""

        self._create_directories()
        self._set_config_file_path()
        self._create_config_file_if_not_present(
                source_path="default_config.ini",
                destination_path=self._config_file_path)

        # Read current config file
        self._parser.read(self._config_file_path)


    def _create_directories(self,) -> None:
        # Create both directories if not present, throws no exception if directories already present
        Path.mkdir((Path.home() / ".barbucket/tw_screener"), parents=True, exist_ok=True)
 

    def _set_config_file_path(self,) -> None:
        self._config_file_path = Path.home() / ".barbucket/config.ini"


    def _create_config_file_if_not_present(self, source_path:Path, destination_path:Path) -> None:
        # Create file with default config if none exists
        if not Path.is_file(destination_path):
            with open(source_path, 'r') as reader:
                default_config = reader.readlines()
            with open(destination_path, 'w') as writer:
                writer.writelines(default_config)


    def get_config_value_single(self, section:str, option:str) -> str:
        """Read a single config value"""

        return self._parser.get(section, option)


    def get_config_value_list(self, section:str, option:str) -> List[str]:
        """Read a config value list"""

        value = self._parser.get(section, option)

        # split by comma and change to list
        value = value.split(",")

        return value
