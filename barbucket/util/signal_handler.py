import signal
import logging
from typing import Any

from barbucket.util.custom_exceptions import ExitSignalDetectedError


_logger = logging.getLogger(__name__)


class SignalHandler():
    """Handle 'Ctrl+C' commands from the user"""

    def __init__(self) -> None:
        signal.signal(signal.SIGINT, self._change_state)
        self._state = False

    def _change_state(self, signum: Any, frame: Any) -> None:
        """Interrupt method, called by system, when Ctrl+C is detected.

        :param signum: [description]
        :type signum: Any
        :param frame: [description]
        :type frame: Any
        """

        _logger.warn(f": Ctrl-C detected, gracefully stopping operation. "
                     f"Press Ctrl-C again to stop immediately.")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self._state = True

    def is_exit_requested(self, throw: bool = False) -> bool:
        """Check if the user pressed Ctrl+C.

        :raises ExitSignalDetectedError: User has pressed 'Ctrl+C'
        """
        if self._state and throw:
            raise ExitSignalDetectedError("User pressed 'Ctrl+C'.")
        return self._state
