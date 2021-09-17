from typing import Any


class ExistingDataIsSufficientError(Exception):
    """Docstring"""


class ExistingDataIsTooOldError(Exception):
    """Docstring"""


class ContractHasErrorStatusError(Exception):
    """Docstring"""


class QueryReturnedNoResultError(Exception):
    """[summary]"""


class QueryReturnedMultipleResultsError(Exception):
    """[summary]"""


class DbNotInitializedError(Exception):
    """Custom exception for connecting to a non-present database."""


class TwsSystemicError(Exception):
    """[summary]"""

    def __init__(self, req_id: int, error_code: int, error_string: str,
                 contract: Any) -> None:
        self.req_id = req_id
        self.error_code = error_code
        self.error_string = error_string
        self.contract = contract


class TwsContractRelatedError(Exception):
    """My custom exception. Parameters are also available."""

    def __init__(self, req_id: int, error_code: int, error_string: str,
                 contract: Any) -> None:
        self.req_id = req_id
        self.error_code = error_code
        self.error_string = error_string
        self.contract = contract


class ExitSignalDetectedError(Exception):
    """"Doc"""
