from pathlib import Path
from logging import getLogger

from barbucket.util.config_reader import ConfigReader


_logger = getLogger(__name__)


class ConnectionStringAssembler():
    """ """

    _config_reader: ConfigReader

    def __init__(self, config_reader: ConfigReader) -> None:
        ConnectionStringAssembler._config_reader = config_reader

    @classmethod
    def get_connection_string(cls) -> str:
        dbms = cls._config_reader.get_config_value_single(
            section="database",
            option="dbms")
        if dbms == "sqlite":
            filename = cls._config_reader.get_config_value_single(
                section="database",
                option="sqlite_filename")
            location = Path.home() / ".barbucket/database/"
            filepath = location / filename
            connection_string = f"sqlite:///{filepath}"
        else:
            username = cls._config_reader.get_config_value_single(
                section="database",
                option="username")
            password = cls._config_reader.get_config_value_single(
                section="database",
                option="password")
            host = cls._config_reader.get_config_value_single(
                section="database",
                option="host")
            port = cls._config_reader.get_config_value_single(
                section="database",
                option="port")
            db_name = cls._config_reader.get_config_value_single(
                section="database",
                option="database_name")
            connection_string = f"{dbms}://{username}:{password}@{host}:{port}/{db_name}"

        _logger.debug(f"Read database connection string from config: "
                      f"'{connection_string}'")
        return connection_string
