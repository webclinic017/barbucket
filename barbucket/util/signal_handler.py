import signal
import logging
from typing import Any


_logger = logging.getLogger(__name__)


class SignalHandler():
    """Handle 'Ctrl+C' commands from the user"""
    _state = False

    def __init__(self) -> None:
        signal.signal(signal.SIGINT, SignalHandler.change_state)

    @classmethod
    def change_state(cls, signum: Any, frame: Any) -> None:
        """Interrupt method, called by system, when Ctrl+C is detected.

        :param signum: [description]
        :type signum: Any
        :param frame: [description]
        :type frame: Any
        """

        _logger.warn(f": Ctrl-C detected, gracefully stopping operation. "
                     f"Press Ctrl-C again to stop immediately.")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        cls._state = True

    @classmethod
    def is_exit_requested(cls) -> None:
        """Check if the user pressed Ctrl+C.

        :raises ExitSignalDetectedError: User has pressed 'Ctrl+C'
        """

        if cls._state:
            raise ExitSignalDetectedError("Message")


class ExitSignalDetectedError(Exception):
    """User has pressed 'Ctrl+C'"""

    def __init__(self, message) -> None:
        self.message = message
        super().__init__(message)
