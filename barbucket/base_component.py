from abc import ABC

from .mediator import Mediator


class BaseComponent(ABC):
    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator
