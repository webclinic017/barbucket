from shutil import copyfile
from pathlib import Path
from logging import getLogger
from typing import List

import pytest

from barbucket.connectionstring_assembler import ConnectionStringAssembler
from barbucket.config.config_reader import ConfigReader


_logger = getLogger(__name__)


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    _logger.debug(f"--------- ---------- Testing ConnectionStringAssembler")


def test_assemble_sqlite():
    # Assemle a connection string for Sqlite
    _logger.debug(f"---------- Test: test_assemble_sqlite")

    filepath = Path.home() / ".barbucket/database/database.sqlite"
    correct_connstring = f"sqlite:///{filepath}"

    config_reader = MockConfigReaderSqlite()
    connstring_assembler = ConnectionStringAssembler(
        config_reader=config_reader)
    connstring = connstring_assembler.get_connection_string()
    assert connstring == correct_connstring


def test_assemble_postgres():
    # Assemle a connection string for PostgreSql
    _logger.debug(f"---------- Test: test_assemble_postgres")

    correct_connstring = "postgresql://username:password@192.168.0.100:5432/barbucket"

    config_reader = MockConfigReaderPostgres()
    connstring_assembler = ConnectionStringAssembler(
        config_reader=config_reader)
    connstring = connstring_assembler.get_connection_string()
    assert connstring == correct_connstring


class MockConfigReaderSqlite(ConfigReader):
    # override
    def __init__(self) -> None:
        pass

    # override
    @classmethod
    def get_config_value_single(cls, section: str, option: str) -> str:
        if (section == "database") and (option == "dbms"):
            return "sqlite"
        elif (section == "database") and (option == "sqlite_filename"):
            return "database.sqlite"
        else:
            raise NotImplementedError

    # override
    @classmethod
    def get_config_value_list(cls, section: str, option: str) -> List[str]:
        raise NotImplementedError


class MockConfigReaderPostgres(ConfigReader):
    # override
    def __init__(self) -> None:
        pass

    # override
    @classmethod
    def get_config_value_single(cls, section: str, option: str) -> str:
        if (section == "database") and (option == "dbms"):
            return "postgresql"
        elif (section == "database") and (option == "username"):
            return "username"
        elif (section == "database") and (option == "password"):
            return "password"
        elif (section == "database") and (option == "host"):
            return "192.168.0.100"
        elif (section == "database") and (option == "port"):
            return "5432"
        elif (section == "database") and (option == "database_name"):
            return "barbucket"
        else:
            raise NotImplementedError

    # override
    @classmethod
    def get_config_value_list(cls, section: str, option: str) -> List[str]:
        raise NotImplementedError
