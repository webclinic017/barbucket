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
            f" Ctrl-C detected, gracefully stopping operation. Press again to "
            f"stop immediately.")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        cls.__state = True

    @classmethod
    def check_exit_requested(cls) -> bool:
        """Check if the user pressed Ctrl-C."""
        return cls.__state
