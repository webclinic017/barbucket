from pathlib import Path
import sqlite3

import pytest

import barbucket.database as database



class MockDatabaseConnector(database.DatabaseConnector):
    pass


@pytest.fixture
def mock_homepath(tmp_path, monkeypatch):
    # Set-up code: create substitution function
    def mock_home():
        return tmp_path

    # substitue original function
    monkeypatch.setattr(Path, "home", mock_home)


@pytest.fixture
def mock_db_connector(mock_homepath) -> MockDatabaseConnector:
    # Set-up object of MockDatabaseConnector class
    mock_db_connector = MockDatabaseConnector()
    mock_db_connector._DB_PATH = Path.home() / "mock_database.sqlite"
    yield mock_db_connector


def test_connect(mock_db_connector) -> None:
    conn = mock_db_connector.connect()
    assert isinstance(conn, sqlite3.dbapi2.Connection)
    mock_db_connector.disconnect(conn)


def test_disconnect(mock_db_connector) -> None:
    conn = mock_db_connector.connect()
    mock_db_connector.disconnect(conn)
    with pytest.raises(sqlite3.ProgrammingError):
        assert conn.cursor()


def test_init_database(mock_db_connector) -> None:
    conn = mock_db_connector.connect()
    mock_db_connector.init_database()

    query = "SELECT name FROM sqlite_master WHERE type='table';"

    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(query)
    tables = cur.fetchall()

    conn.commit()
    cur.close()
    mock_db_connector.disconnect(conn)

    # schema = 
    
    # assert tables == 
