from typing import Any


class ExistingDataIsSufficientError(Exception):
    """Docstring"""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)


class ExistingDataIsTooOldError(Exception):
    """Docstring"""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)


class ContractHasErrorStatusError(Exception):
    """Docstring"""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)


class QueryReturnedNoResultError(Exception):
    """[summary]"""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)


class QueryReturnedMultipleResultsError(Exception):
    """[summary]"""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)


class NotInitializedError(Exception):
    """Custom exception for connecting to a non-present database."""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)


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

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)
