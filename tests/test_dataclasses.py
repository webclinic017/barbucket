from typing import Generator
from logging import getLogger

import pytest
from sqlalchemy.orm import Session

from barbucket.data_classes import *
from barbucket.orm_connector import OrmConnector


_logger = getLogger(__name__)


@pytest.fixture(scope="module", autouse=True)
def setup_module():
    _logger.debug(f"--------- ---------- Testing DataClasses")


class MockOrmConnector(OrmConnector):
    # override
    def __init__(self) -> None:
        pass

    # override
    @classmethod
    def get_session(cls) -> Session:
