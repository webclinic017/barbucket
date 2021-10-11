import signal
import logging
from typing import Any

from barbucket.mediator import Mediator

logger = logging.getLogger(__name__)


class SignalHandler():

    def __init__(self, mediator: Mediator = None) -> None:
        self.state = False
        signal.signal(signal.SIGINT, self.change_state)
        self.mediator = mediator

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
