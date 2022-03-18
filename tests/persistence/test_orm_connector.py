from typing import Generator
from logging import getLogger

import pytest
from sqlalchemy import select, inspect, Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Session, declarative_base, relationship

from barbucket.persistence.orm_connector import OrmConnector
from barbucket.persistence.connectionstring_assembler import ConnectionStringAssembler


_logger = getLogger(__name__)
_logger.debug(f"--------- ---------- Testing OrmConnector")
TestBase = declarative_base()


@pytest.fixture
def orm_connector() -> Generator:
    _logger.debug(f"---------- Fixture: orm_connector")

    class MockConnectionStringAssembler(ConnectionStringAssembler):
        # override
        def __init__(self) -> None:
            pass

        # override
        @classmethod
        def get_connection_string(cls) -> str:
            return "sqlite:///:memory:"

    oc = OrmConnector(
        connstring_assembler=MockConnectionStringAssembler(),
        base_class=TestBase)
    yield oc


@pytest.fixture
def dummy_one() -> Generator:
    _logger.debug(f"---------- Fixture: dummy_one")

    dummy = DummyClassOne(
        string_column="Test_string",
        integer_column=12345,
        float_column=678.99)
    yield dummy


class DummyClassOne(TestBase):
    __tablename__ = 'dummy_objects_one'

    id = Column(Integer, primary_key=True)
    string_column = Column(String(30))
    integer_column = Column(Integer)
    float_column = Column(Float)

    UniqueConstraint('string_column', 'integer_column')

    dummy_two = relationship(
        "DummyClassTwo",
        back_populates="dummy_one",
        cascade="all, delete",
        passive_deletes=True)

    def __repr__(self):
        return f"""DummyClassOne(
            id={self.id},
            string_column={self.string_column},
            integer_column={self.integer_column},
            float_column={self.float_column})"""


@pytest.fixture
def dummy_two(dummy_one) -> Generator:
    _logger.debug(f"---------- Fixture: dummy_two")

    dummy = DummyClassTwo(
        string_column="Test_string",
        integer_column=12345,
        float_column=678.99,
        dummy_one=dummy_one)
    yield dummy


class DummyClassTwo(TestBase):
    __tablename__ = 'dummy_objects_two'

    dummy_one_id = Column(
        Integer,
        ForeignKey('dummy_objects_one.id', ondelete="CASCADE"),
        primary_key=True)
    string_column = Column(String(30))
    integer_column = Column(Integer)
    float_column = Column(Float)

    UniqueConstraint('integer_column', 'float_column')

    dummy_one = relationship(
        "DummyClassOne", back_populates="dummy_two")

    def __repr__(self):
        return f"""UniverseMembership(
            string_column={self.string_column},
            integer_column={self.integer_column},
            float_column={self.float_column},
            dummy_one={self.dummy_one})"""


def test_get_session(
        orm_connector: OrmConnector,
        dummy_two: DummyClassTwo) -> None:
    _logger.debug(f"---------- Test: test_get_session")
    session = orm_connector.get_session()
    assert type(session) == Session


def test_tables_present(
        orm_connector: OrmConnector,
        dummy_two: DummyClassTwo) -> None:
    _logger.debug(f"---------- Test: test_tables_present")
    expected_tables = ['dummy_objects_one', 'dummy_objects_two']
    actual_tables = inspect(orm_connector._engine).get_table_names()
    assert all([exp in actual_tables for exp in expected_tables])
    assert len(actual_tables) == len(expected_tables)


def test_insert_one(
        orm_connector: OrmConnector,
        dummy_two: DummyClassTwo) -> None:
    _logger.debug(f"---------- Test: test_insert_one")
    session = orm_connector.get_session()
    dummy_one = dummy_two.dummy_one
    session.add(dummy_one)
    session.commit()
    assert dummy_one.id == 1


def test_insert_both(
        orm_connector: OrmConnector,
        dummy_two: DummyClassTwo) -> None:
    _logger.debug(f"---------- Test: test_insert_both")
    session = orm_connector.get_session()
    session.add(dummy_two)
    session.commit()
    assert dummy_two.dummy_one_id == 1
    assert dummy_two.dummy_one.id == 1


def test_retrieve_one(
        orm_connector: OrmConnector,
        dummy_two: DummyClassTwo) -> None:
    _logger.debug(f"---------- Test: test_retrieve_one")
    session = orm_connector.get_session()
    dummy_one = dummy_two.dummy_one
    session.add(dummy_one)
    session.commit()
    returned_one = session.execute(select(DummyClassOne)).scalar_one()
    assert returned_one is dummy_one


def test_retrieve_both(
        orm_connector: OrmConnector,
        dummy_two: DummyClassTwo) -> None:
    _logger.debug(f"---------- Test: test_retrieve_both")
    session = orm_connector.get_session()
    dummy_one = dummy_two.dummy_one
    session.add(dummy_two)
    session.commit()
    returned_two = session.execute(select(DummyClassTwo)).scalar_one()
    assert returned_two is dummy_two
    assert returned_two.dummy_one is dummy_one


def test_delete_one(
        orm_connector: OrmConnector,
        dummy_two: DummyClassTwo) -> None:
    _logger.debug(f"---------- Test: test_delete_one")
    session = orm_connector.get_session()
    dummy_one = dummy_two.dummy_one
    session.add(dummy_one)
    session.commit()
    assert dummy_one.id == 1
    session.delete(dummy_one)
    returned_one = session.execute(select(DummyClassOne)).scalars().all()
    assert len(returned_one) == 0


def test_delete_both(
        orm_connector: OrmConnector,
        dummy_two: DummyClassTwo) -> None:
    _logger.debug(f"---------- Test: test_delete_both")
    session = orm_connector.get_session()
    dummy_one = dummy_two.dummy_one
    session.add(dummy_two)
    session.commit()
    assert dummy_two.dummy_one.id == 1
    session.delete(dummy_one)
    returned_one = session.execute(select(DummyClassOne)).scalars().all()
    assert len(returned_one) == 0
    returned_two = session.execute(select(DummyClassTwo)).scalars().all()
    assert len(returned_two) == 0
