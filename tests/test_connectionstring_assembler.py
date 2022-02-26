from shutil import copyfile
from pathlib import Path

from barbucket.connectionstring_assembler import ConnectionStringAssembler
from barbucket.config_reader import ConfigReader


def test_assemble_sqlite(tmp_path):
    filepath = Path.home() / ".barbucket/database/database.sqlite"
    correct_connstring = f"sqlite:///{filepath}"

    src = "tests/resources/config_sqlite.cfg"
    dst = tmp_path / "config.cfg"
    copyfile(src, dst)
    config_reader = ConfigReader(filepath=dst)
    connstring_assembler = ConnectionStringAssembler(
        config_reader=config_reader)
    connstring = connstring_assembler.get_connection_string()
    assert connstring == correct_connstring


def test_assemble_postgres(tmp_path):
    correct_connstring = "postgresql://username:password@192.168.0.100:5432/barbucket"

    src = "tests/resources/config_postgres.cfg"
    dst = tmp_path / "config.cfg"
    copyfile(src, dst)
    config_reader = ConfigReader(filepath=dst)
    connstring_assembler = ConnectionStringAssembler(
        config_reader=config_reader)
    connstring = connstring_assembler.get_connection_string()
    assert connstring == correct_connstring
