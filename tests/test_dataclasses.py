from typing import Generator
from logging import getLogger
from datetime import date

import pytest
from sqlalchemy import select

from barbucket.data_classes import *
from barbucket.orm_connector import OrmConnector


_logger = getLogger(__name__)


@pytest.fixture(scope="module", autouse=True)
def setup_module() -> None:
    _logger.debug(f"--------- ---------- Testing DataClasses")


# ~~~~~~~~~~~~~~~~~~~~~~~~ Contract ~~~~~~~~~~~~~~~~~~~~~~~~


@pytest.fixture
def dummy_contract() -> Generator:
    _logger.debug(f"---------- Fixture: dummy_contract")
    contract = Contract(
        contract_type_from_listing="test_contract_type_from_listing",
        exchange_symbol="test_exchange_symbol",
        broker_sybmol="test_broker_sybmol",
        name="test_name",
        currency="test_currency",
        exchange="test_exchange")
    yield contract


def test_write_contract(orm_connector: OrmConnector, dummy_contract: Contract) -> None:
    _logger.debug(f"---------- Test: test_write_contract")
    session = orm_connector.get_session()
    session.add(dummy_contract)
    session.commit()
    assert dummy_contract.id == 1


def test_read_contract(orm_connector: OrmConnector, dummy_contract: Contract) -> None:
    _logger.debug(f"---------- Test: test_read_contract")
    session = orm_connector.get_session()
    session.add(dummy_contract)
    session.commit()
    read_contract = session.execute(select(Contract)).scalar_one()
    assert read_contract is dummy_contract


# ~~~~~~~~~~~~~~~~~~~~~~~~ UniverseMembership ~~~~~~~~~~~~~~~~~~~~~~~~


@pytest.fixture
def dummy_univ_membership(dummy_contract) -> Generator:
    _logger.debug(f"---------- Fixture: dummy_univ_membership")
    membership = UniverseMembership(
        universe="test_universe",
        contract=dummy_contract)
    yield membership


def test_write_universe_membership(orm_connector: OrmConnector, dummy_univ_membership: UniverseMembership) -> None:
    _logger.debug(f"---------- Test: test_write_universe_membership")
    session = orm_connector.get_session()
    session.add(dummy_univ_membership)
    session.commit()
    assert dummy_univ_membership.id == 1


def test_read_universe_membership(orm_connector: OrmConnector, dummy_univ_membership: UniverseMembership) -> None:
    _logger.debug(f"---------- Test: test_read_universe_membership")
    session = orm_connector.get_session()
    session.add(dummy_univ_membership)
    session.commit()
    read_membership = session.execute(select(UniverseMembership)).scalar_one()
    assert read_membership is dummy_univ_membership
    assert read_membership.contract is dummy_univ_membership.contract


# ~~~~~~~~~~~~~~~~~~~~~~~~ ContractDetailsIb ~~~~~~~~~~~~~~~~~~~~~~~~


@pytest.fixture
def dummy_contract_details_ib(dummy_contract) -> Generator:
    _logger.debug(f"---------- Fixture: dummy_contract_details_ib")
    details = ContractDetailsIb(
        contract_type_from_details="test_contract_type_from_details",
        primary_exchange="test_primary_exchange",
        industry="test_industry",
        category="test_category",
        subcategory="test_subcategory",
        contract=dummy_contract)
    yield details


def test_write_contract_details_ib(orm_connector: OrmConnector, dummy_contract_details_ib: ContractDetailsIb) -> None:
    _logger.debug(f"---------- Test: test_write_contract_details_ib")
    session = orm_connector.get_session()
    session.add(dummy_contract_details_ib)
    session.commit()
    assert dummy_contract_details_ib.contract_id == 1


def test_read_contract_details_ib(orm_connector: OrmConnector, dummy_contract_details_ib: ContractDetailsIb) -> None:
    _logger.debug(f"---------- Test: test_read_contract_details_ib")
    session = orm_connector.get_session()
    session.add(dummy_contract_details_ib)
    session.commit()
    read_details = session.execute(select(ContractDetailsIb)).scalar_one()
    assert read_details is dummy_contract_details_ib
    assert read_details.contract is dummy_contract_details_ib.contract


# ~~~~~~~~~~~~~~~~~~~~~~~~ ContractDetailsTv ~~~~~~~~~~~~~~~~~~~~~~~~


@pytest.fixture
def dummy_contract_details_tv(dummy_contract) -> Generator:
    _logger.debug(f"---------- Fixture: dummy_contract_details_tv")
    details = ContractDetailsTv(
        market_cap=1111,
        avg_vol_30_in_curr=2222,
        country="test_country",
        employees=3333,
        profit=4444,
        revenue=5555,
        contract=dummy_contract)
    yield details


def test_write_contract_details_tv(orm_connector: OrmConnector, dummy_contract_details_tv: ContractDetailsTv) -> None:
    _logger.debug(f"---------- Test: test_write_contract_details_tv")
    session = orm_connector.get_session()
    session.add(dummy_contract_details_tv)
    session.commit()
    assert dummy_contract_details_tv.contract_id == 1


def test_read_contract_details_tv(orm_connector: OrmConnector, dummy_contract_details_tv: ContractDetailsTv) -> None:
    _logger.debug(f"---------- Test: test_read_contract_details_tv")
    session = orm_connector.get_session()
    session.add(dummy_contract_details_tv)
    session.commit()
    read_details = session.execute(select(ContractDetailsTv)).scalar_one()
    assert read_details is dummy_contract_details_tv
    assert read_details.contract is dummy_contract_details_tv.contract


# ~~~~~~~~~~~~~~~~~~~~~~~~ QuotesStatus ~~~~~~~~~~~~~~~~~~~~~~~~


@pytest.fixture
def dummy_quotes_status(dummy_contract) -> Generator:
    _logger.debug(f"---------- Fixture: dummy_quotes_status")
    details = QuotesStatus(
        status_code=1111,
        status_text="test_status_text",
        earliest_quote_requested=date.today(),
        latest_quote_requested=date.today(),
        contract=dummy_contract)
    yield details


def test_write_quotes_status(orm_connector: OrmConnector, dummy_quotes_status: QuotesStatus) -> None:
    _logger.debug(f"---------- Test: test_write_quotes_status")
    session = orm_connector.get_session()
    session.add(dummy_quotes_status)
    session.commit()
    assert dummy_quotes_status.contract_id == 1


def test_read_quotes_status(orm_connector: OrmConnector, dummy_quotes_status: QuotesStatus) -> None:
    _logger.debug(f"---------- Test: test_read_quotes_status")
    session = orm_connector.get_session()
    session.add(dummy_quotes_status)
    session.commit()
    read_status = session.execute(select(QuotesStatus)).scalar_one()
    assert read_status is dummy_quotes_status
    assert read_status.contract is dummy_quotes_status.contract


# ~~~~~~~~~~~~~~~~~~~~~~~~ Quote ~~~~~~~~~~~~~~~~~~~~~~~~


@pytest.fixture
def dummy_quote(dummy_contract) -> Generator:
    _logger.debug(f"---------- Fixture: dummy_quote")
    details = Quote(
        date=date.today(),
        open=222.22,
        high=333.33,
        low=444.44,
        close=555.55,
        volume=666.66,
        contract=dummy_contract)
    yield details


def test_write_quote(orm_connector: OrmConnector, dummy_quote: Quote) -> None:
    _logger.debug(f"---------- Test: test_write_quote")
    session = orm_connector.get_session()
    session.add(dummy_quote)
    session.commit()
    assert dummy_quote.contract_id == 1


def test_read_quote(orm_connector: OrmConnector, dummy_quote: Quote) -> None:
    _logger.debug(f"---------- Test: test_read_quote")
    session = orm_connector.get_session()
    session.add(dummy_quote)
    session.commit()
    read_quote = session.execute(select(Quote)).scalar_one()
    assert read_quote is dummy_quote
    assert read_quote.contract is dummy_quote.contract
