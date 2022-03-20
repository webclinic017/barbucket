from pathlib import Path
from typing import Generator
from shutil import copyfile
from logging import getLogger

import pytest

from barbucket.util.config_reader import ConfigReader


_logger = getLogger(__name__)
_logger.debug(f"--------- ---------- Testing ConfigReader")


@pytest.fixture
def mock_filepath(tmp_path: Path) -> Generator:
    """Creating temp path for config file"""
    _logger.debug(f"---------- Fixture: mock_filepath")
    filepath = tmp_path / ".barbucket/config.cfg"
    yield filepath


@pytest.fixture
def dummy_filepath(mock_filepath: Path) -> Generator:
    """Creating mock config file"""
    _logger.debug(f"---------- Fixture: dummy_file")
    dummy_file = "tests/_resources/config/config_dummy.cfg"
    Path.mkdir(mock_filepath.parent, parents=True, exist_ok=True)
    copyfile(dummy_file, mock_filepath)
    yield mock_filepath


def test_copy_default_file(mock_filepath: Path) -> None:
    # Make sure, the default config file is copied, when no config file is present
    _logger.debug(f"---------- Test: test_copy_default_file")
    assert not mock_filepath.is_file()
    config_reader = ConfigReader(filepath=mock_filepath)
    assert mock_filepath.is_file()


def test_file_already_existing(dummy_filepath: Path) -> None:
    """
    Make sure, existing config file is not altered by ConfigReader 
    initialization
    """
    _logger.debug(f"---------- Test: test_file_already_existing")
    with open(dummy_filepath, 'r') as reader:
        content_before = reader.readlines()
    config_reader = ConfigReader(filepath=dummy_filepath)
    with open(dummy_filepath, 'r') as reader:
        content_after = reader.readlines()
    assert content_after == content_before


def test_read_single_value(dummy_filepath: Path) -> None:
    _logger.debug(f"---------- Test: test_read_single_value")
    config_reader = ConfigReader(filepath=dummy_filepath)
    value = config_reader.get_config_value_single(
        section="section_1",
        option="option_11")
    assert value == "MyString"


def test_read_list_value(dummy_filepath: Path) -> None:
    _logger.debug(f"---------- Test: test_read_list_value")
    config_reader = ConfigReader(filepath=dummy_filepath)
    value = config_reader.get_config_value_list(
        section="section_2",
        option="option_21")
    assert value == ["11", "22", "Something", "33.4"]
