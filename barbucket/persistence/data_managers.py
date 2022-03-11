from typing import List
import logging
from datetime import date

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from barbucket.domain_model.data_classes import\
    Contract, UniverseMembership, ContractDetailsIb, ContractDetailsTv, Quote


_logger = logging.getLogger(__name__)


class UniverseDbManager():
    def __init__(self, orm_session: Session) -> None:
        self._orm_session = orm_session

    def get_members(self, universe: str) -> List[Contract]:
        statement = (select(UniverseMembership)
                     .where(UniverseMembership.universe == universe))
        result = self._orm_session.execute(statement).scalars()
        members = [row.contract for row in result]
        _logger.debug(f"Read {len(result)} members for universe '{universe}' "
                      f"from database with session '{self._orm_session}'.")
        return members


class ContractsDbManager():
    def __init__(self, orm_session: Session) -> None:
        self._orm_session = orm_session

    def is_existing(self, contract: Contract) -> bool:
        statement = (select(Contract.id).where(and_(
            Contract.broker_symbol == contract.broker_symbol,
            Contract.currency == contract.currency,
            Contract.exchange == contract.exchange)))
        count = self._orm_session.execute(statement).count()
        _logger.debug(f"Found {count} entries for Contract '{contract}' with "
                      f"session '{self._orm_session}'")
        if count > 1:
            pass  # todo: raise exception
        return bool(count)

    def write_to_db(self, contract: Contract) -> None:
        self._orm_session.add(contract)
        _logger.debug(f"Added Contract '{contract}' to session "
                      f"'{self._orm_session}'")

    def get_one_by_filters(self, filters) -> Contract:
        statement = (select(Contract).where(and_(*filters)))
        contract = self._orm_session.execute(statement).scalar_one()
        filters_string = ", ".join([str(f) for f in filters])
        _logger.debug(f"Read Contract '{contract}' from database for filters "
                      f"'{filters_string}' with session '{self._orm_session}'.")
        return contract

    def get_by_filters(self, filters) -> List[Contract]:
        statement = (select(Contract).where(and_(*filters)))
        contracts = self._orm_session.execute(statement).scalars().all()
        filters_string = ", ".join([str(f) for f in filters])
        _logger.debug(f"Read {len(contracts)} contracts from database for "
                      f"filters '{filters_string}' with session "
                      f"'{self._orm_session}'.")
        return contracts

    def delete(self, contract: Contract) -> None:
        self._orm_session.delete(contract)
        _logger.debug(f"Deleted Contract '{contract}' with session "
                      f"'{self._orm_session}'")


# class QuotesStatusDbManager():
#     def __init__(self, orm_session: Session) -> None:
#         self._orm_session = orm_session

#     def read_from_db(self, contract: Contract) -> QuotesStatus:
#         statement = (select(QuotesStatus)
#                      .where(QuotesStatus.contract == contract))
#         count = self._orm_session.execute(statement).count()
#         if count == 0:
#             self._create_new_status(contract)
#         status = self._orm_session.execute(statement).scalar_one()
#         _logger.debug(f"Read QuoteStatus '{status}' from database with session "
#                       f"'{self._orm_session}'.")
#         return status

#     def write_to_db(self, status: QuotesStatus) -> None:
#         self._orm_session.add(status)
#         _logger.debug(f"Added QuotesStatus '{status}' to session "
#                       f"'{self._orm_session}'")

#     def _create_new_status(self, contract: Contract) -> None:
#         new_status = QuotesStatus(
#             status_code=0,
#             status_text="No quotes downloaded yet.")
#         self._orm_session.add(new_status)
#         _logger.debug(f"Created new QuotesStatus '{new_status}' for contract "
#                       f"'{contract}' in session '{self._orm_session}'.")


class QuotesDbManager():
    def __init__(self, orm_session: Session) -> None:
        self._orm_session = orm_session

    def write_to_db(self, quotes: List[Quote]) -> None:
        # Needs to overwrite existing quotes
        contract = quotes[0].contract
        existing_quotes = self._orm_session.execute(
            select(Quote).where(Quote.contract == contract)).scalars().all()
        for quote in quotes:
            if quote in existing_quotes:
                quote_to_update = self._orm_session.execute(select(Quote).
                                                            where(and_(Quote.contract == contract,
                                                                       Quote.date == quote.date)))
                quote_to_update.open = quote.open
                quote_to_update.high = quote.high
                quote_to_update.low = quote.low
                quote_to_update.close = quote.close
                quote_to_update.volume = quote.volume
            else:
                self._orm_session.add(quote)
        _logger.debug(f"Added {len(quotes)} quotes to session "
                      f"'{self._orm_session}'. Last quote is '{quotes[-1]}'")

    def contract_has_quotes(self, contract: Contract) -> bool:
        statement = (select(Quote.contract_id).where(
            Quote.contract == contract))
        count = self._orm_session.execute(statement).count()
        return bool(count)

    def get_latest_quote_date(self, contract: Contract) -> date:
        statement = select(Quote.date).\
            where(Quote.contract == contract).\
            order_by(Quote.date.desc())
        quote = self._orm_session.execute(statement).first().scalar()
        return quote.date


class ContractDetailsIbDbManager():
    _orm_session: Session

    def __init__(self, orm_session: Session) -> None:
        self._orm_session = orm_session

    def write_to_db(self, details: ContractDetailsIb) -> None:
        self._orm_session.add(details)
        _logger.debug(f"Added ContractDetailsIb '{details}' to session "
                      f"'{self._orm_session}'")


class ContractDetailsTvDbManager():
    def __init__(self, orm_session: Session) -> None:
        self._orm_session = orm_session

    def write_to_db(self, details: ContractDetailsTv) -> None:
        self._orm_session.add(details)
        _logger.debug(f"Added ContractDetailsTv '{details}' to session "
                      f"'{self._orm_session}'")
