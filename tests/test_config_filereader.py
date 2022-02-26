from pathlib import Path
from typing import Generator
from shutil import copyfile
from logging import getLogger

import pytest

from barbucket.config.config_filereader import ConfigFilereader


_logger = getLogger(__name__)


@pytest.fixture(scope="module", autouse=True)
def setup_module() -> None:
    _logger.debug(f"--------- ---------- Testing ConfigReader")


@pytest.fixture
def filepath(tmp_path: Path) -> Generator:
    # Creating temp path for config file
    _logger.debug(f"---------- Fixture: tmp_path")
    filepath = tmp_path / "config.cfg"
    yield filepath


def test_copy_default_file(filepath: Path) -> None:
    # Make sure, the default config file is copied, when no config file is present
    _logger.debug(f"---------- Test: test_copy_default_file")
    assert not filepath.is_file()
    config_reader = ConfigFilereader(filepath=filepath)
    assert filepath.is_file()


def test_file_already_existing(filepath: Path) -> None:
    # Make sure, existing config file is not altered by ConfigReader initialization
    _logger.debug(f"---------- Test: test_file_already_existing")
    testfile = "tests/resources/config_dummy.cfg"
    with open(testfile, 'r') as reader:
        content_before = reader.readlines()
    copyfile(testfile, filepath)
    config_reader = ConfigFilereader(filepath=filepath)
    with open(filepath, 'r') as reader:
        content_after = reader.readlines()
    assert content_after == content_before


def test_read_single_value(filepath: Path) -> None:
    _logger.debug(f"---------- Test: test_read_single_value")
    copyfile("tests/resources/config_dummy.cfg", filepath)
    config_reader = ConfigFilereader(filepath=filepath)
    value = config_reader.get_config_value_single(
        section="section_1",
        option="option_11")
    assert value == "MyString"


def test_read_list_value(filepath: Path) -> None:
    _logger.debug(f"---------- Test: test_read_list_value")
    copyfile("tests/resources/config_dummy.cfg", filepath)
    config_reader = ConfigFilereader(filepath=filepath)
    value = config_reader.get_config_value_list(
        section="section_2",
        option="option_21")
    assert value == ["11", "22", "Something", "33.4"]
