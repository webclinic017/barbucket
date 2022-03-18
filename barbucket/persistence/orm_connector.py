from logging import getLogger

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.orm.decl_api import DeclarativeMeta

from barbucket.persistence.connectionstring_assembler import ConnectionStringAssembler


_logger = getLogger(__name__)


class OrmConnector():
    """ """

    def __init__(
            self,
            connstring_assembler: ConnectionStringAssembler,
            base_class: DeclarativeMeta) -> None:
        self._connstring_assembler = connstring_assembler
        self._base_class = base_class
        self._initialize()

    def get_session(self) -> Session:
        """_summary_

        :return: _description_
        :rtype: Session
        """
        return self._session

    # ~~~~~~~~~~~~~~~~ private methods ~~~~~~~~~~~~~~~~

    def _initialize(self) -> None:
        conn_string = self._connstring_assembler.get_connection_string()
        self._engine = create_engine(conn_string, future=True)
        self._add_sqlite_pragma()
        self._create_db_schema()
        self._session = Session(self._engine)

    def _add_sqlite_pragma(self) -> None:
        # Adding foreign key pragma on every connection for sqlite by event
        def _fk_pragma_on_connect(dbapi_con, con_record):
            dbapi_con.execute('PRAGMA foreign_keys = 1')

        if self._engine.url.drivername == 'sqlite':
            event.listen(self._engine, 'connect', _fk_pragma_on_connect)
            _logger.debug("Added FOREIGN_KEY pragma event for sqlite within "
                          f"engine '{self._engine}'.")

    def _create_db_schema(self) -> None:
        self._base_class.metadata.create_all(self._engine)
        _logger.debug(
            f"Created database schema within engine '{self._engine}'.")
