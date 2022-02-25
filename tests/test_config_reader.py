from pathlib import Path
from typing import Generator

import pytest

from barbucket.config_reader import ConfigReader


@pytest.fixture
def filepath(tmp_path: Path) -> Generator:
    filepath = tmp_path / "default_config.cfg"
    yield filepath


@pytest.fixture
def config_reader(filepath: Path) -> Generator:
    yield ConfigReader(filepath=filepath)


def test_copy_default_file(filepath, config_reader) -> None:
    assert filepath.is_file()


def test_file_already_existing():
    pass


def test_read_single_value(config_reader):
    value = config_reader.get_config_value_single(
        section="database",
        option="dbms")
    assert value == "sqlite"


def test_read_list_value(config_reader):
    value = config_reader.get_config_value_list(
        section="tws_connector",
        option="non_systemic_codes")
    assert value == ["162", "200", "354", "2104", "2106", "2107", "2158"]
