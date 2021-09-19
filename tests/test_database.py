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


def create_db_file(path: Path) -> None:
    # create database file
    conn = sqlite3.connect(path)
    conn.close()


def test_connect_existing(mock_db_connector) -> None:
    # create file
    create_db_file(mock_db_connector._DB_PATH)

    # connect
    conn = mock_db_connector.connect()
    assert isinstance(conn, sqlite3.dbapi2.Connection)
    mock_db_connector.disconnect(conn)


def test_connect_nonexisting(mock_db_connector) -> None:
    with pytest.raises(database.NotInitializedError):
        assert mock_db_connector.connect()


def test_disconnect(mock_db_connector) -> None:
    # create file
    create_db_file(mock_db_connector._DB_PATH)

    # connect
    conn = mock_db_connector.connect()

    # disconnect
    mock_db_connector.disconnect(conn)
    with pytest.raises(sqlite3.ProgrammingError):
        assert conn.cursor()


def test_archive_database_existing(mock_db_connector) -> None:
    # create file
    create_db_file(mock_db_connector._DB_PATH)

    # archive
    mock_db_connector.archive_database()

    assert not Path.is_file(mock_db_connector._DB_PATH)


def test_archive_database_nonexisting(mock_db_connector) -> None:
    with pytest.raises(FileNotFoundError):
        assert mock_db_connector.archive_database()


def test_init_database_existing(mock_db_connector) -> None:
    # create file
    create_db_file(mock_db_connector._DB_PATH)

    # call init method
    mock_db_connector.init_database()

    # test if did not crash
    assert True


def test_init_database_nonexisting(mock_db_connector) -> None:
    mock_db_connector.init_database()
    conn = mock_db_connector.connect()

    query = "SELECT name FROM sqlite_master WHERE type='table';"

    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute(query)
    tables = cur.fetchall()

    conn.commit()
    cur.close()
    mock_db_connector.disconnect(conn)

    assert len(tables) == 6
