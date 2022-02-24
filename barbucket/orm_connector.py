from abc import ABC

from sqlalchemy.orm import Session


class OrmConnector(ABC):

    def get_session(self) -> Session:
        raise NotImplementedError
