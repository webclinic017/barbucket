import signal
import logging
from typing import Any


logger = logging.getLogger(__name__)


class SignalHandler():
    __state = False

    def __init__(self) -> None:
        signal.signal(signal.SIGINT, SignalHandler.change_state)

    @classmethod
    def change_state(cls, signum: Any, frame: Any) -> None:
        """Interrupt method, called by system, when Ctrl-C is detected."""

        logger.warn(
            f": Ctrl-C detected, gracefully stopping operation. Press again to "
            f"stop immediately.")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        cls.__state = True

    @classmethod
    def is_exit_requested(cls) -> None:
        """Check if the user pressed Ctrl+C.

        :raises ExitSignalDetectedError: User has pressed 'Ctrl+C'
        """

        if cls.__state:
            raise ExitSignalDetectedError("Message")


class ExitSignalDetectedError(Exception):
    """"Doc"""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)
