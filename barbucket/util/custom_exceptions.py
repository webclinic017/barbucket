class InvalidDataReceivedError(Exception):
    """"Doc"""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)


class ExitSignalDetectedError(Exception):
    """User has pressed 'Ctrl+C'"""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)
