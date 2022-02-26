from abc import ABC, abstractmethod
from typing import List


class ConfigReader(ABC):

    @abstractmethod
    def get_config_value_single(cls, section: str, option: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_config_value_list(cls, section: str, option: str) -> List[str]:
        raise NotImplementedError
