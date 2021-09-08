from abc import ABC
from typing import Any


class BaseComponent(ABC):
    def __init__(self, mediator: Any = None) -> None:
        self.mediator = mediator
