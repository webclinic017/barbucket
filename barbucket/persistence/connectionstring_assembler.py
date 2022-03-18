from pathlib import Path
from logging import getLogger

from barbucket.util.config_reader import ConfigReader


_logger = getLogger(__name__)


class ConnectionStringAssembler():
    """ """

    def __init__(self, config_reader: ConfigReader) -> None:
        self._config_reader = config_reader

    def get_connection_string(self) -> str:
        dbms = self._config_reader.get_config_value_single(
            section="database",
            option="dbms")
        if dbms == "sqlite":
            filename = self._config_reader.get_config_value_single(
                section="database",
                option="sqlite_filename")
            location = Path.home() / ".barbucket/"
            filepath = location / filename
            connection_string = f"sqlite:///{filepath}"
        else:
            username = self._config_reader.get_config_value_single(
                section="database",
                option="username")
            password = self._config_reader.get_config_value_single(
                section="database",
                option="password")
            host = self._config_reader.get_config_value_single(
                section="database",
                option="host")
            port = self._config_reader.get_config_value_single(
                section="database",
                option="port")
            db_name = self._config_reader.get_config_value_single(
                section="database",
                option="database_name")
            connection_string = f"{dbms}://{username}:{password}@{host}:{port}/{db_name}"

        _logger.debug(f"Read database connection string from config: "
                      f"'{connection_string}'")
        return connection_string
