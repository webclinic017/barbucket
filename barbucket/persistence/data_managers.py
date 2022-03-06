from typing import List, Dict
import logging

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from barbucket.domain_model.data_classes import *


_logger = logging.getLogger(__name__)


class UniverseMembershipsDbManager():
    _db_session: Session

    def __init__(self, db_session: Session) -> None:
        UniverseMembershipsDbManager._db_session = db_session

    @classmethod
    def get_members(cls, universe: str) -> List[Contract]:
        statement = (select(UniverseMembership)
                     .where(UniverseMembership.universe == universe))
        result = cls._db_session.execute(statement).scalars()
        members = [row.contract for row in result]
        _logger.debug(f"Read {len(result)} members for universe '{universe}' "
                      f"from database with session '{cls._db_session}'.")
        return members


class ContractsDbManager():
    _db_session: Session

    def __init__(self, db_session: Session) -> None:
        ContractsDbManager._db_session = db_session

    @classmethod
    def is_existing(cls, contract: Contract) -> bool:
        statement = (select(Contract.id).where(
            Contract.broker_sybmol == contract.broker_sybmol,
            Contract.currency == contract.currency,
            Contract.exchange == contract.exchange))
        count = cls._db_session.execute(statement).count()
        _logger.debug(f"Found {count} entries for Contract '{contract}' with "
                      f"session '{cls._db_session}'")
        if count > 1:
            pass  # todo: raise exception
        return bool(count)

    @ classmethod
    def write_to_db(cls, contract: Contract) -> None:
        cls._db_session.add(contract)
        _logger.debug(f"Added Contract '{contract}' to session "
                      f"'{cls._db_session}'")

    @ classmethod
    def get_one_by_filters(cls, filters) -> Contract:
        statement = (select(Contract).where(and_(*filters)))
        contract = cls._db_session.execute(statement).scalar_one()
        filters_string = ", ".join([str(f) for f in filters])
        _logger.debug(f"Read Contract '{contract}' from database for filters "
                      f"'{filters_string}' with session '{cls._db_session}'.")
        return contract

    @ classmethod
    def get_by_filters(cls, filters) -> List[Contract]:
        statement = (select(Contract).where(and_(*filters)))
        contracts = cls._db_session.execute(statement).scalars().all()
        filters_string = ", ".join([str(f) for f in filters])
        _logger.debug(f"Read {len(contracts)} contracts from database for "
                      f"filters '{filters_string}' with session "
                      f"'{cls._db_session}'.")
        return contracts

    @ classmethod
    def delete(cls, contract: Contract) -> None:
        cls._db_session.delete(contract)
        _logger.debug(f"Deleted Contract '{contract}' with session "
                      f"'{cls._db_session}'")


class QuotesStatusDbManager():
    _db_session: Session

    def __init__(self, db_session: Session) -> None:
        QuotesStatusDbManager._db_session = db_session

    @ classmethod
    def read_from_db(cls, contract: Contract) -> QuotesStatus:
        statement = (select(QuotesStatus)
                     .where(QuotesStatus.contract == contract))
        count = cls._db_session.execute(statement).count()
        if count == 0:
            cls._create_new_status(contract)
        status = cls._db_session.execute(statement).scalar_one()
        _logger.debug(f"Read QuoteStatus '{status}' from database with session "
                      f"'{cls._db_session}'.")
        return status

    @ classmethod
    def write_to_db(cls, status: QuotesStatus) -> None:
        cls._db_session.add(status)
        _logger.debug(f"Added QuotesStatus '{status}' to session "
                      f"'{cls._db_session}'")

    @ classmethod
    def _create_new_status(cls, contract: Contract) -> None:
        new_status = QuotesStatus(
            status_code=0,
            status_text="No quotes downloaded yet.")
        cls._db_session.add(new_status)
        _logger.debug(f"Created new QuotesStatus '{new_status}' for contract "
                      f"'{contract}' in session '{cls._db_session}'.")


class QuotesDbManager():
    _db_session: Session

    def __init__(self, db_session: Session) -> None:
        QuotesDbManager._db_session = db_session

    @ classmethod
    def write_to_db(cls, quotes: List[Quote]) -> None:
        for quote in quotes:
            cls._db_session.add(quote)
        _logger.debug(f"Added {len(quotes)} quotes to session "
                      f"'{cls._db_session}'. Last quote is '{quotes[-1]}'")


class ContractDetailsIbDbManager():
    _db_session: Session

    def __init__(self, db_session: Session) -> None:
        ContractDetailsIbDbManager._db_session = db_session

    @ classmethod
    def write_to_db(cls, details: ContractDetailsIb) -> None:
        cls._db_session.add(details)
        _logger.debug(f"Added ContractDetailsIb '{details}' to session "
                      f"'{cls._db_session}'")


class ContractDetailsTvDbManager():
    _db_session: Session

    def __init__(self, db_session: Session) -> None:
        ContractDetailsTvDbManager._db_session = db_session

    @ classmethod
    def write_to_db(cls, details: ContractDetailsTv) -> None:
        cls._db_session.add(details)
        _logger.debug(f"Added ContractDetailsTv '{details}' to session "
                      f"'{cls._db_session}'")
