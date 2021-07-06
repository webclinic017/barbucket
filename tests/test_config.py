import pytest
import barbucket.config as config
from pathlib import Path


# @pytest.fixture
# def return_object_name():
#     """Fixture template"""
#
#     # Set-up code
#     my_object = MyClass()
#     yield my_object
#
#     # Tear-down code
#     pass


class MockConfig(config.Config):
    def __init__(self) -> None:
        # Read default config file
        self._parser.read("default_config.ini")


@pytest.fixture
def mock_cfg():
    # Set-up object of MockConfig class
    mock_conf = MockConfig()
    yield mock_conf


@pytest.fixture
def mock_homepath(tmp_path, monkeypatch):
    # Set-up code
    # create substitution function
    def mock_home():
        return tmp_path

    # substitue original function
    monkeypatch.setattr(Path, "home", mock_home)


def test_create_directories_if_not_present(mock_cfg, mock_homepath):
    mock_cfg.create_directories()
    assert Path.is_dir(Path.home() / ".barbucket/tw_screener")


def test_create_directories_if_one_present(mock_cfg, mock_homepath):
    Path.mkdir(Path.home() / ".barbucket")
    mock_cfg.create_directories()
    assert Path.is_dir(Path.home() / ".barbucket/tw_screener")


def test_create_directories_if_both_present(mock_cfg, mock_homepath):
    Path.mkdir((Path.home() / ".barbucket/tw_screener"), parents=True)
    mock_cfg.create_directories()
    assert Path.is_dir(Path.home() / ".barbucket/tw_screener")


def test_set_config_file_path(mock_cfg, mock_homepath):
    mock_cfg.set_config_file_path()
    assert mock_cfg._config_file_path == Path.home() / ".barbucket/config.ini"


def test_create_config_file_if_not_present(mock_cfg, mock_homepath):
    Path.mkdir(Path.home() / ".barbucket")
    mock_cfg.create_config_file_if_not_present(
            source_path="default_config.ini",
            destination_path=(Path.home() / ".barbucket/config.ini")
    )
    with open("default_config.ini", 'r') as reader_default:
        default_config = reader_default.readlines()
    with open((Path.home() / ".barbucket/config.ini"), 'r') as reader_new:
        new_config = reader_new.readlines()
    assert default_config == new_config


def test_get_config_value_single(mock_cfg):
    value = mock_cfg.get_config_value_single('database', 'db_location')
    assert value == ".barbucket/database.db"


def test_get_config_value_list(mock_cfg):
    value = mock_cfg.get_config_value_list('tws_connector', 'non_systemic_codes')
    assert value == ["162", "200", "354", "2104", "2106", "2107", "2158"]