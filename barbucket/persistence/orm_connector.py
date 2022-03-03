from logging import getLogger

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.engine import Engine

from .connectionstring_assembler import ConnectionStringAssembler


_logger = getLogger(__name__)


class OrmConnector():
    """ """

    _connstring_assembler: ConnectionStringAssembler
    _engine: Engine
    _session: Session
    _base_class: DeclarativeMeta

    def __init__(
            self,
            connstring_assembler: ConnectionStringAssembler,
            base_class: DeclarativeMeta) -> None:
        OrmConnector._connstring_assembler = connstring_assembler
        OrmConnector._base_class = base_class
        OrmConnector._initialize()

    @classmethod
    def get_session(cls) -> Session:
        """_summary_

        :return: _description_
        :rtype: Session
        """
        return cls._session

    # ~~~~~~~~~~~~~~~~ private methods ~~~~~~~~~~~~~~~~

    @classmethod
    def _initialize(cls) -> None:
        conn_string = cls._connstring_assembler.get_connection_string()
        cls._engine = create_engine(conn_string, future=True)
        cls._add_sqlite_pragma()
        cls._create_db_schema()
        cls._session = Session(cls._engine)

    @classmethod
    def _add_sqlite_pragma(cls) -> None:
        # Adding foreign key pragma on every connection for sqlite by event
        def _fk_pragma_on_connect(dbapi_con, con_record):
            dbapi_con.execute('PRAGMA foreign_keys = 1')

        if cls._engine.url.drivername == 'sqlite':
            event.listen(cls._engine, 'connect', _fk_pragma_on_connect)
            _logger.debug("Added FOREIGN_KEY pragma event for sqlite within "
                          f"engine '{cls._engine}'.")

    @classmethod
    def _create_db_schema(cls) -> None:
        cls._base_class.metadata.create_all(cls._engine)
        _logger.debug(
            f"Created database schema within engine '{cls._engine}'.")
