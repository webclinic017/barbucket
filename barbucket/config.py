import configparser
from pathlib import Path


class Config():

    _parser = configparser.ConfigParser(allow_no_value=True)
    _config_file_path = None


    def __init__(self,):
        """
        Prepare config file and read content
        """

        self.create_directories_if_not_present()

        self.set_config_file_path()

        self.create_config_file_if_not_present(
                source_path="default_config.ini",
                destination_path=self._config_file_path)

        # Read current config file
        self._parser.read(self._config_file_path)


    def create_directories_if_not_present(self,):

        if not Path.is_dir(Path.home() / ".barbucket"):
            Path.mkdir(Path.home() / ".barbucket")
        if not Path.is_dir(Path.home() / ".barbucket/tw_screener"):
            Path.mkdir(Path.home() / ".barbucket/tw_screener")


    def set_config_file_path(self,):
        self._config_file_path = Path.home() / ".barbucket/config.ini"


    def create_config_file_if_not_present(self, source_path, destination_path):

        # Create file with default config if none exists
        if not Path.is_file(destination_path):
            with open(source_path, 'r') as reader:
                default_config = reader.readlines()
            with open(destination_path, 'w') as writer:
                writer.writelines(default_config)


    def get_config_value(self, section, option):
        """
        Read a config value
        """

        value = self._parser.get(section, option)

        #If value contains comma, split by comma and change to list
        if "," in value:
            value = value.split(",")

        return value


