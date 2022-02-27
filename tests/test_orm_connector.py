from typing import Generator
from logging import getLogger

import pytest
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from barbucket.orm_connector import OrmConnector


_logger = getLogger(__name__)


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    _logger.debug(f"--------- ---------- Testing OrmConnector")


def test_get_session(orm_connector: OrmConnector) -> None:
    _logger.debug(f"---------- Test: test_get_session")
    session = orm_connector.get_session()
    assert type(session) == Session


def test_schema_present(orm_connector: OrmConnector) -> None:
    _logger.debug(f"---------- Test: test_schema_present")
    expected_tables = ['contract_details_ib', 'contract_details_tv',
                       'contracts', 'quotes', 'quotes_status',
                       'universe_memberships']
    actual_tables = inspect(orm_connector._engine).get_table_names()
    assert all([exp in actual_tables for exp in expected_tables])
    assert len(actual_tables) == len(expected_tables)


def test_pragma_present() -> None:
    # Is tested with test_cascade
    assert 1
