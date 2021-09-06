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
