from typing import List

from sqlalchemy.orm import Session

from data_classes import Contract


class UniverseMembershipsDbManager():
    _db_session: Session

    def __init__(self, db_session: Session) -> None:
        UniverseMembershipsDbManager._db_session = db_session

    def get_members(self, universe: str) -> List[Contract]:
        pass


class ContractsDbManager():
    _db_session: Session

    def __init__(self, db_session: Session) -> None:
        ContractsDbManager._db_session = db_session


class QuotesStatusDbManager():
    _db_session: Session

    def __init__(self, db_session: Session) -> None:
        QuotesStatusDbManager._db_session = db_session


class QuotesDbManager():
    _db_session: Session

    def __init__(self, db_session: Session) -> None:
        QuotesDbManager._db_session = db_session


class ContractDetailsIbDbManager():
    _db_session: Session

    def __init__(self, db_session: Session) -> None:
        ContractDetailsIbDbManager._db_session = db_session


class ContractDetailsTvDbManager():
    _db_session: Session

    def __init__(self, db_session: Session) -> None:
        ContractDetailsTvDbManager._db_session = db_session
