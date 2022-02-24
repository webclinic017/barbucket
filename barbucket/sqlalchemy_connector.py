from ast import Str
from pathlib import Path
from logging import getLogger

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine

from .config_reader import ConfigReader
from .orm_connector import OrmConnector
from data_classes import Base

logger = getLogger(__name__)


class SqlAlchemyConnector(OrmConnector):
    """ """

    _config_reader: ConfigReader
    _engine: Engine
    _session: Session

    def __init__(self, config_reader) -> None:
        SqlAlchemyConnector._config_reader = config_reader
        conn_string = SqlAlchemyConnector._get_connection_string()
        SqlAlchemyConnector._engine = create_engine(conn_string)
        SqlAlchemyConnector._add_sqlite_pragma()
        SqlAlchemyConnector._create_db_schema()
        SqlAlchemyConnector._session = Session(SqlAlchemyConnector._engine)

    @classmethod
    def get_session(cls) -> Session:
        """_summary_

        :return: _description_
        :rtype: Session
        """
        return cls._session

    # ~~~~~~~~~~~~~~~~ private methods ~~~~~~~~~~~~~~~~

    @classmethod
    def _get_connnection_string(cls) -> Str:
        dbms = cls._config_reader.get_config_value_single(
            section="database",
            option="dbms")
        if dbms == "sqlite":
            filename = cls._config_reader.get_config_value_single(
                section="database",
                option="sqlite_filename")
            filepath = ".barbucket/database/" + filename
            filepath = Path.home() / ".barbucket/database/"
            connection_string = dbms + ":///" + filepath
        else:
            username = cls._config_reader.get_config_value_single(
                section="database",
                option="username")
            password = cls._config_reader.get_config_value_single(
                section="database",
                option="password")
            url = cls._config_reader.get_config_value_single(
                section="database",
                option="url")
            port = cls._config_reader.get_config_value_single(
                section="database",
                option="port")
            db_name = cls._config_reader.get_config_value_single(
                section="database",
                option="database_name")
            connection_string = f"{dbms}://{username}:{password}@{url}:{port}/{db_name}"

        logger.debug(
            f"Read database connection string fromn config: '{connection_string}'")
        return connection_string

    @classmethod
    def _add_sqlite_pragma(cls) -> None:
        # Adding foreign key pragma on every connection for sqlite by event
        def _fk_pragma_on_connect(dbapi_con, con_record):
            dbapi_con.execute('PRAGMA foreign_keys = 1')
        # can this be called in this scope?

        if cls._engine.url.drivername == 'sqlite':
            event.listen(cls._engine, 'connect', _fk_pragma_on_connect)
            print("Added FOREIGN_KEY pragma event for sqlite.")

    @classmethod
    def _create_db_schema(cls) -> None:
        Base.metadata.create_all(cls._engine)
