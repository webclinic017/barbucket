from pathlib import Path
from typing import Generator
from shutil import copyfile

import pytest

from barbucket.config_reader import ConfigReader


@pytest.fixture
def filepath(tmp_path: Path) -> Generator:
    filepath = tmp_path / "config.cfg"
    yield filepath


def test_copy_default_file(filepath) -> None:
    config_reader = ConfigReader(filepath=filepath)
    assert filepath.is_file()


def test_file_already_existing(filepath):
    testfile = "tests/resources/config_dummy.cfg"
    with open(testfile, 'r') as reader:
        content_before = reader.readlines()
    copyfile(testfile, filepath)
    config_reader = ConfigReader(filepath=filepath)
    with open(filepath, 'r') as reader:
        content_after = reader.readlines()
    assert content_after == content_before


def test_read_single_value(filepath):
    copyfile("tests/resources/config_dummy.cfg", filepath)
    config_reader = ConfigReader(filepath=filepath)
    value = config_reader.get_config_value_single(
        section="section_1",
        option="option_11")
    assert value == "MyString"


def test_read_list_value(filepath):
    copyfile("tests/resources/config_dummy.cfg", filepath)
    config_reader = ConfigReader(filepath=filepath)
    value = config_reader.get_config_value_list(
        section="section_2",
        option="option_21")
    assert value == ["11", "22", "Something", "33.4"]
