import pytest
import barbucket.config as cfg
from pathlib import Path
import configparser


### Fixture template
# @pytest.fixture
# def return_object_name():
#     # Set-up code
#     object = None
#     yield object
#     # Tear-down code
#     pass


def test_init_config_file(mock_homepath):
    # Run code
    cfg.init_config_file()

    # Create configparser and read file
    parser = configparser.ConfigParser(allow_no_value=True)
    path = Path.home() / ".barbucket/config.ini"
    parser.read(path)

    for section in cfg.__default_config:
        options = cfg.__default_config[section]
        for option in options:
            code_value = cfg.__default_config[section][option]
            file_value = parser.get(section, option)
            assert code_value == file_value


def test_get_config_value(mock_homepath):
    test_config = {
    'section_1': {
        'option_11': "123",
        'option 12!': "-123.45",
        'option 12!': "0"},
    'section_2': {
        'option_21': "123,456",
        '\# Comment': "",
        'option 22!': "Lorem Ipsum"}}

    # Create configparser
    parser = configparser.ConfigParser(allow_no_value=True)

    # Write test configuration to file
    path = Path.home()
    if not Path.is_dir(path / ".barbucket"):
        Path.mkdir(path / ".barbucket")
    path = Path.home() / ".barbucket/config.ini"
    parser.read_dict(test_config)
    with open(path, 'w') as file:
        parser.write(file)

    # Read test configuration from file and assert
    for section in test_config:
        options = test_config[section]
        for option in options:
            code_value = test_config[section][option]
            file_value = cfg.get_config_value(section, option)
            if "," in code_value:
                assert code_value.split(",") == file_value
            else:
                assert code_value == file_value


