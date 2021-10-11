import signal
import logging
from typing import Any


logger = logging.getLogger(__name__)


class SignalHandler():

    def __init__(self) -> None:
        self.state = False
        signal.signal(signal.SIGINT, self.change_state)

    def change_state(self, signum: Any, frame: Any) -> None:
        """Interrupt method, called by system, when Ctrl-C is detected."""

        logger.warn(
            f"Ctrl-C detected, gracefully stopping operation. Press again to "
            f"stop immediately.")
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.state = True

    def exit_requested(self) -> bool:
        """Check if the user pressed Ctrl-C."""
        return self.state
