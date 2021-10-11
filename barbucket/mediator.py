from typing import Optional, Any

from . import cli as cli


class Mediator():
    """Mediator"""

    def __init__(
            self,
            cli: Any) -> None:

        # Instanciate components
        self.__tws_connector.mediator = self

        self.__cli = cli
        self.__cli.cli_connector.mediator = self

    def notify(self, action: str, parameters: dict = {}) -> Optional[object]:
        # Cli
        if action == "run_cli":
            return self.__cli.cli()
        elif action == "show_cli_message":
            return self.__cli.show_messeage(
                message=parameters['message'])
