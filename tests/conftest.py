import pytest
from pathlib import Path

from barbucket.database import DatabaseCreator


### Fixture template
# @pytest.fixture
# def return_object_name():
#     # Set-up code
#     object = None
#     yield object
#     # Tear-down code
#     pass


@pytest.fixture
def mock_homepath(tmp_path, monkeypatch):
    # Set-up code
    # create substitution function
    def mock_home():
        return tmp_path

    # substitue original function
    monkeypatch.setattr(Path, "home", mock_home)


@pytest.fixture
def create_database(mock_homepath):
    db_creator = DatabaseCreator()
    db_creator._create_database()