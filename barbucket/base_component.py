from abc import ABC


class BaseComponent(ABC):
    def __init__(self, mediator: Mediator = None) -> None:
        self.mediator = mediator
