import sqlite3
from pathlib import Path


class DatabaseConnector():
    DB_PATH = Path.home() / ".barbucket/database.db"
    # Todo: Follow dependency injection principle

    def __init__(self):
        pass


    def connect(self):
        conn = sqlite3.connect(DatabaseConnector.DB_PATH)
        conn.execute("""
            PRAGMA foreign_keys = 1;
        """)
        return conn


    def disconnect(self, conn):
        conn.close()
